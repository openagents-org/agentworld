#!/usr/bin/env python3
"""
Task Evaluator for AgentWorld Benchmark
Runs Claude to evaluate all tasks in parallel and aggregates results.
"""

import os
import sys
import subprocess
import argparse
import json
import re
import time
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class EvaluationResult:
    task_id: str  # Can be int or string like "01_magic_staff_v1"
    solvability: Optional[str] = None
    plausibility: Optional[str] = None
    diversity: Optional[str] = None
    justification: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0


class TaskEvaluator:
    def __init__(
        self,
        base_dir: str = "/home/ubuntu/works/agentworld",
        results_dir: str = "evaluate_results",
        max_workers: int = 5,
        timeout: int = 180,
        dataset: str = "benchmark",  # "benchmark" or "augmented"
    ):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / results_dir
        self.dataset = dataset

        # Select dataset directory
        if dataset == "augmented":
            self.benchmark_dir = self.base_dir / "data_v0.1_multi" / "v1.3_augmented"
        else:
            self.benchmark_dir = self.base_dir / "data_v0.1_multi" / "v1.3_benchmark"

        self.docs_dir = self.base_dir / "docs"
        self.max_workers = max_workers
        self.timeout = timeout

        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Pre-load docs for reference
        self.docs_content = self._load_docs()

    def _load_docs(self) -> str:
        """Load relevant documentation files."""
        docs = []
        doc_files = ["crafting.md", "mobs.md", "regions.md", "game_tools.md"]
        for doc_file in doc_files:
            doc_path = self.docs_dir / doc_file
            if doc_path.exists():
                content = doc_path.read_text()
                # Truncate if too long
                if len(content) > 3000:
                    content = content[:3000] + "\n... (truncated)"
                docs.append(f"## {doc_file}\n{content}")
        return "\n\n".join(docs)

    def get_task_files(self) -> List[Path]:
        """Get all task files from the dataset directory."""
        return sorted(self.benchmark_dir.glob("task_*.yaml"))

    def get_task_ids(self) -> List[str]:
        """Get all task IDs from the dataset directory.
        For augmented dataset, returns full identifiers like '01_magic_staff_v1'.
        For benchmark, returns just task numbers.
        """
        task_files = self.get_task_files()
        task_ids = []
        for f in task_files:
            if self.dataset == "augmented":
                # Extract full identifier: task_01_magic_staff_v1.yaml -> 01_magic_staff_v1
                match = re.search(r'task_(.+)\.yaml', f.name)
                if match:
                    task_ids.append(match.group(1))
            else:
                # Extract just the number
                match = re.search(r'task_(\d+)_', f.name)
                if match:
                    task_ids.append(int(match.group(1)))
        return sorted(set(task_ids), key=lambda x: str(x))

    def _load_task(self, task_id) -> Optional[Dict]:
        """Load task YAML content."""
        task_file = self._get_task_file(task_id)
        if task_file:
            with open(task_file) as f:
                return yaml.safe_load(f)
        return None

    def _get_task_file(self, task_id) -> Optional[Path]:
        """Get task file path."""
        if self.dataset == "augmented":
            # For augmented: task_id is like "01_magic_staff_v1"
            pattern = f"task_{task_id}.yaml"
            files = list(self.benchmark_dir.glob(pattern))
        else:
            # For benchmark: task_id is an integer
            pattern = f"task_{task_id:02d}_*.yaml"
            files = list(self.benchmark_dir.glob(pattern))
            if not files:
                pattern = f"task_{task_id}_*.yaml"
                files = list(self.benchmark_dir.glob(pattern))
        return files[0] if files else None

    def generate_prompt(self, task_id: int, task_content: str) -> str:
        """Generate the evaluation prompt with pre-loaded task content."""
        return f"""You are a task evaluator for a multi-agent game environment called AgentWorld.
Evaluate the following task based on three criteria.

IMPORTANT: DO NOT use any tools. All information you need is provided below. Just analyze and respond directly.

=== TASK {task_id} CONTENT ===
{task_content}

=== GAME DOCUMENTATION (REFERENCE) ===
{self.docs_content[:6000]}

=== EVALUATION CRITERIA ===
1. **Solvability**: Can this task be completed by the specified agents within the max_action_steps?
   Consider: agent skill levels, required crafting recipes, travel distances, boss difficulty.
   Answer: YES or NO

2. **Plausibility**: Does this task genuinely require collaboration among multiple agents?
   Consider: Can one agent do everything alone? Are different skills distributed across agents?
   Answer: Good (requires collaboration) or Bad (single agent could do it)

3. **Diversity**: Does this task show variety in skills, actions, or coordination patterns?
   Consider: Does it combine multiple activities (combat, crafting, gathering)? Is it unique?
   Answer: Good (diverse/creative) or Bad (repetitive/simple)

=== YOUR RESPONSE (use this exact format - respond directly without using tools) ===
### Evaluation Result
TASK {task_id} | Solvability: <YES/NO> | Plausibility: <Good/Bad> | Diversity: <Good/Bad>

### Justification
- Solvability: <1-2 sentences>
- Plausibility: <1-2 sentences>
- Diversity: <1-2 sentences>
"""

    def evaluate_task(self, task_id: int) -> EvaluationResult:
        """Evaluate a single task using Claude CLI."""
        result = EvaluationResult(task_id=task_id)
        start_time = time.time()

        # Load task content
        task_file = self._get_task_file(task_id)
        if not task_file:
            result.error = f"Task file not found for task {task_id}"
            result.duration = time.time() - start_time
            return result

        task_content = task_file.read_text()
        prompt = self.generate_prompt(task_id, task_content)

        try:
            # Run Claude CLI with the prompt - use print mode for direct output
            cmd = [
                "claude",
                "-p", prompt,
                "--output-format", "text",
                "--max-turns", "8"  # Allow up to 8 turns for evaluation (more for file reading)
            ]

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.base_dir)
            )

            result.duration = time.time() - start_time
            output = proc.stdout

            if output:
                result = self.parse_result(output, result)
                # Save the result to file
                self.save_result(task_id, output)
            else:
                result.error = f"No output. stderr: {proc.stderr[:200] if proc.stderr else 'None'}"

        except subprocess.TimeoutExpired:
            result.duration = time.time() - start_time
            result.error = f"Timeout after {self.timeout}s"
        except Exception as e:
            result.duration = time.time() - start_time
            result.error = str(e)

        return result

    def parse_result(self, content: str, result: EvaluationResult) -> EvaluationResult:
        """Parse evaluation result from content."""
        # Extract the evaluation line - try multiple patterns
        patterns = [
            # Match: TASK xxx | Solvability: YES | Plausibility: Good | Diversity: Good
            r'TASK\s+[\w_]+\s*\|\s*Solvability:\s*(YES|NO)\s*\|\s*Plausibility:\s*(Good|Bad)\s*\|\s*Diversity:\s*(Good|Bad)',
            # Match inline format
            r'Solvability:\s*(YES|NO)\s*\|\s*Plausibility:\s*(Good|Bad)\s*\|\s*Diversity:\s*(Good|Bad)',
            # Match with any word (fallback)
            r'Solvability:\s*(\w+).*?Plausibility:\s*(\w+).*?Diversity:\s*(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                solv = match.group(1).upper()
                plau = match.group(2).capitalize()
                div = match.group(3).capitalize()

                result.solvability = "YES" if "YES" in solv else ("NO" if "NO" in solv else solv)
                result.plausibility = "Good" if "GOOD" in plau.upper() else ("Bad" if "BAD" in plau.upper() else plau)
                result.diversity = "Good" if "GOOD" in div.upper() else ("Bad" if "BAD" in div.upper() else div)
                break

        # Extract justification
        just_patterns = [
            r'### Justification\s*(.*?)(?=###|$)',
            r'Justification[:\s]*(.*?)$',
            r'- Solvability:(.*?)(?=###|$)',
        ]

        for pattern in just_patterns:
            just_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if just_match:
                result.justification = just_match.group(1).strip()[:500]
                break

        return result

    def save_result(self, task_id, content: str):
        """Save result to file."""
        # Handle both int and string task IDs
        if isinstance(task_id, int):
            filename = f"task_{task_id:03d}.md"
        else:
            filename = f"task_{task_id}.md"
        output_file = self.results_dir / filename
        output_file.write_text(content)

    def run_all(self, task_ids: Optional[List[int]] = None) -> List[EvaluationResult]:
        """Run evaluation for all tasks in parallel."""
        if task_ids is None:
            task_ids = self.get_task_ids()

        results = []
        total = len(task_ids)
        completed = 0

        print(f"Starting evaluation of {total} tasks with {self.max_workers} workers...")
        print(f"Results will be saved to: {self.results_dir}")
        print("-" * 60)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self.evaluate_task, tid): tid
                for tid in task_ids
            }

            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1

                    status = "✓" if result.error is None and result.solvability else "✗"
                    solv = result.solvability or "?"
                    plau = result.plausibility or "?"
                    div = result.diversity or "?"

                    # Format task_id for display
                    if isinstance(task_id, int):
                        task_str = f"{task_id:03d}"
                    else:
                        task_str = str(task_id)[:25]  # Truncate long names

                    print(f"[{completed}/{total}] {task_str} {status} | "
                          f"Solv: {solv:<3} | Plau: {plau:<4} | Div: {div:<4} | "
                          f"Time: {result.duration:.1f}s")

                except Exception as e:
                    completed += 1
                    result = EvaluationResult(task_id=task_id, error=str(e))
                    results.append(result)
                    print(f"[{completed}/{total}] Task {task_id:03d} ✗ Error: {e}")

        return results

    def aggregate_results(self, results: List[EvaluationResult]) -> Dict:
        """Aggregate evaluation results into summary statistics."""
        summary = {
            "total_tasks": len(results),
            "evaluated": 0,
            "errors": 0,
            "solvability": {"YES": 0, "NO": 0, "UNKNOWN": 0},
            "plausibility": {"Good": 0, "Bad": 0, "Unknown": 0},
            "diversity": {"Good": 0, "Bad": 0, "Unknown": 0},
            "avg_duration": 0.0,
            "timestamp": datetime.now().isoformat(),
            "tasks": []
        }

        total_duration = 0.0

        for r in results:
            task_info = {
                "task_id": r.task_id,
                "solvability": r.solvability,
                "plausibility": r.plausibility,
                "diversity": r.diversity,
                "duration": r.duration,
                "error": r.error
            }
            summary["tasks"].append(task_info)
            total_duration += r.duration

            if r.error:
                summary["errors"] += 1
            else:
                summary["evaluated"] += 1

                # Count solvability
                if r.solvability == "YES":
                    summary["solvability"]["YES"] += 1
                elif r.solvability == "NO":
                    summary["solvability"]["NO"] += 1
                else:
                    summary["solvability"]["UNKNOWN"] += 1

                # Count plausibility
                if r.plausibility == "Good":
                    summary["plausibility"]["Good"] += 1
                elif r.plausibility == "Bad":
                    summary["plausibility"]["Bad"] += 1
                else:
                    summary["plausibility"]["Unknown"] += 1

                # Count diversity
                if r.diversity == "Good":
                    summary["diversity"]["Good"] += 1
                elif r.diversity == "Bad":
                    summary["diversity"]["Bad"] += 1
                else:
                    summary["diversity"]["Unknown"] += 1

        if summary["total_tasks"] > 0:
            summary["avg_duration"] = total_duration / summary["total_tasks"]

        return summary

    def save_summary(self, summary: Dict, filename: str = "evaluation_summary.json"):
        """Save aggregated summary to JSON file."""
        output_file = self.results_dir / filename
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\nSummary saved to: {output_file}")
        return output_file

    def print_summary(self, summary: Dict):
        """Print summary statistics to console."""
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Tasks:     {summary['total_tasks']}")
        print(f"Evaluated:       {summary['evaluated']}")
        print(f"Errors:          {summary['errors']}")
        print(f"Avg Duration:    {summary['avg_duration']:.1f}s")
        print("-" * 60)
        print("SOLVABILITY:")
        yes_pct = summary['solvability']['YES'] / max(summary['evaluated'], 1) * 100
        print(f"  YES:     {summary['solvability']['YES']} ({yes_pct:.1f}%)")
        print(f"  NO:      {summary['solvability']['NO']}")
        print(f"  Unknown: {summary['solvability']['UNKNOWN']}")
        print("-" * 60)
        print("PLAUSIBILITY:")
        good_pct = summary['plausibility']['Good'] / max(summary['evaluated'], 1) * 100
        print(f"  Good:    {summary['plausibility']['Good']} ({good_pct:.1f}%)")
        print(f"  Bad:     {summary['plausibility']['Bad']}")
        print(f"  Unknown: {summary['plausibility']['Unknown']}")
        print("-" * 60)
        print("DIVERSITY:")
        good_pct = summary['diversity']['Good'] / max(summary['evaluated'], 1) * 100
        print(f"  Good:    {summary['diversity']['Good']} ({good_pct:.1f}%)")
        print(f"  Bad:     {summary['diversity']['Bad']}")
        print(f"  Unknown: {summary['diversity']['Unknown']}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate AgentWorld benchmark tasks using Claude"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default="/home/ubuntu/works/agentworld",
        help="Base directory of AgentWorld"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="evaluate_results",
        help="Directory to save evaluation results"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel workers (default: 5)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Timeout per task in seconds (default: 180)"
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default=None,
        help="Comma-separated list of task IDs to evaluate (e.g., '1,2,3' or '01_magic_staff_v1'). Default: all tasks"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="Start task ID for range evaluation (benchmark only)"
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="End task ID for range evaluation (benchmark only)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["benchmark", "augmented"],
        default="benchmark",
        help="Dataset to evaluate: 'benchmark' (100 tasks) or 'augmented' (200 tasks)"
    )

    args = parser.parse_args()

    # Adjust results directory based on dataset
    results_dir = args.results_dir
    if args.dataset == "augmented" and results_dir == "evaluate_results":
        results_dir = "evaluate_results_augmented"

    evaluator = TaskEvaluator(
        base_dir=args.base_dir,
        results_dir=results_dir,
        max_workers=args.workers,
        timeout=args.timeout,
        dataset=args.dataset
    )

    print(f"Dataset: {args.dataset} ({evaluator.benchmark_dir})")

    # Determine which tasks to evaluate
    task_ids = None
    if args.tasks:
        # For augmented dataset, keep as strings; for benchmark, try to parse as int
        if args.dataset == "augmented":
            task_ids = [t.strip() for t in args.tasks.split(",")]
        else:
            task_ids = [int(t.strip()) for t in args.tasks.split(",")]
    elif args.start is not None or args.end is not None:
        if args.dataset == "augmented":
            print("Warning: --start/--end only work with benchmark dataset. Using all tasks.")
        else:
            all_tasks = evaluator.get_task_ids()
            start = args.start or min(all_tasks)
            end = args.end or max(all_tasks)
            task_ids = [t for t in all_tasks if start <= t <= end]

    # Run evaluations
    results = evaluator.run_all(task_ids)

    # Aggregate and save summary
    summary = evaluator.aggregate_results(results)
    evaluator.save_summary(summary)
    evaluator.print_summary(summary)

    # Generate CSV report
    csv_file = evaluator.results_dir / "evaluation_results.csv"
    with open(csv_file, 'w') as f:
        f.write("task_id,solvability,plausibility,diversity,duration,error\n")
        for r in sorted(results, key=lambda x: x.task_id):
            error = r.error.replace('"', '""') if r.error else ""
            f.write(f'{r.task_id},{r.solvability or ""},{r.plausibility or ""},{r.diversity or ""},{r.duration:.1f},"{error}"\n')
    print(f"CSV report saved to: {csv_file}")

    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
