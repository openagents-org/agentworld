#!/usr/bin/env python3
"""
Beam Search Task Verification - CLI Entry Point

Usage:
    # Single task
    python -m beam_verifier.main --task path/to/task.yaml

    # Batch run
    python -m beam_verifier.main --folder path/to/tasks/

    # With options
    python -m beam_verifier.main --task task.yaml --beam-size 2 --max-steps 25
"""

import argparse
import json
import os
import sys
import glob
from pathlib import Path
from typing import List, Dict, Any

from .beam_search import BeamSearchVerifier, VerificationResult, run_single_task


def run_batch(
    folder_path: str,
    beam_size: int,
    max_steps: int,
    api_base: str,
    output_dir: str = None,
    verbose: bool = False
) -> Dict[str, VerificationResult]:
    """
    Run verification on all tasks in a folder.

    Args:
        folder_path: Path to folder containing task YAMLs
        beam_size: Beam size for search
        max_steps: Maximum steps per task
        api_base: API base URL
        output_dir: Directory to save results (optional)
        verbose: Print progress for each task

    Returns:
        Dictionary mapping task_id to VerificationResult
    """
    # Find all YAML files
    yaml_pattern = os.path.join(folder_path, "*.yaml")
    task_files = sorted(glob.glob(yaml_pattern))

    if not task_files:
        print(f"No YAML files found in {folder_path}")
        return {}

    print(f"Found {len(task_files)} tasks")
    print("=" * 60)

    results = {}
    success_count = 0
    total_steps = 0
    total_time = 0

    for i, task_path in enumerate(task_files):
        task_id = Path(task_path).stem
        print(f"\n[{i+1}/{len(task_files)}] Running: {task_id}")

        try:
            result = run_single_task(
                task_path=task_path,
                beam_size=beam_size,
                max_steps=max_steps,
                api_base=api_base,
                verbose=verbose
            )

            results[task_id] = result

            status = "SUCCESS" if result.success else "FAILED"
            print(f"  Result: {status} in {result.steps_taken} steps "
                  f"({result.elapsed_time:.1f}s)")

            if result.success:
                success_count += 1
            total_steps += result.steps_taken
            total_time += result.elapsed_time

            # Save individual result if output_dir specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                result_path = os.path.join(output_dir, f"{task_id}_result.json")
                with open(result_path, 'w') as f:
                    json.dump(result.to_dict(), f, indent=2, default=str)

        except Exception as e:
            print(f"  Error: {str(e)}")
            results[task_id] = VerificationResult(
                success=False,
                steps_taken=0,
                final_states={},
                action_history=[],
                verifier_message=f"Error: {str(e)}",
                task_id=task_id
            )

    # Print summary
    print("\n" + "=" * 60)
    print("BATCH SUMMARY")
    print("=" * 60)
    print(f"Total tasks: {len(task_files)}")
    print(f"Successful: {success_count} ({100*success_count/len(task_files):.1f}%)")
    print(f"Failed: {len(task_files) - success_count}")
    print(f"Total steps: {total_steps}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Average time: {total_time/len(task_files):.1f}s per task")

    # Save batch summary
    if output_dir:
        summary_path = os.path.join(output_dir, "batch_summary.json")
        summary = {
            'total_tasks': len(task_files),
            'successful': success_count,
            'failed': len(task_files) - success_count,
            'success_rate': success_count / len(task_files),
            'total_steps': total_steps,
            'total_time': total_time,
            'average_time': total_time / len(task_files),
            'results': {
                task_id: {
                    'success': r.success,
                    'steps': r.steps_taken,
                    'time': r.elapsed_time,
                    'message': r.verifier_message
                }
                for task_id, r in results.items()
            }
        }
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\nResults saved to: {output_dir}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Beam Search Task Verification for AgentWorld',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single task
  python -m beam_verifier.main --task data_v0.1_multi/v1.3_benchmark/task_01_magic_staff.yaml

  # Run all tasks in folder
  python -m beam_verifier.main --folder data_v0.1_multi/v1.3_benchmark/ --output results/

  # Custom settings
  python -m beam_verifier.main --task task.yaml --beam-size 3 --max-steps 30 --verbose
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--task',
        help='Path to single task YAML file'
    )
    input_group.add_argument(
        '--folder',
        help='Path to folder containing task YAMLs (for batch run)'
    )

    # Algorithm options
    parser.add_argument(
        '--beam-size',
        type=int,
        default=2,
        help='Beam size for search (default: 2)'
    )
    parser.add_argument(
        '--max-steps',
        type=int,
        default=25,
        help='Maximum steps before giving up (default: 25)'
    )

    # API options
    parser.add_argument(
        '--api-base',
        default='http://localhost:7031',
        help='Base URL for simulation API (default: http://localhost:7031)'
    )

    # Output options
    parser.add_argument(
        '--output',
        help='Output path for results (file for single, directory for batch)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed progress'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output (only final result)'
    )

    args = parser.parse_args()

    # Determine verbosity
    verbose = args.verbose and not args.quiet

    if args.task:
        # Single task mode
        if not os.path.exists(args.task):
            print(f"Error: Task file not found: {args.task}")
            sys.exit(1)

        result = run_single_task(
            task_path=args.task,
            beam_size=args.beam_size,
            max_steps=args.max_steps,
            api_base=args.api_base,
            verbose=not args.quiet
        )

        # Output result
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            print(f"\nResult saved to: {args.output}")
        elif not args.quiet:
            print("\n" + "=" * 60)
            print("RESULT")
            print("=" * 60)
            print(json.dumps(result.to_dict(), indent=2, default=str))

        # Exit code based on success
        sys.exit(0 if result.success else 1)

    else:
        # Batch mode
        if not os.path.isdir(args.folder):
            print(f"Error: Folder not found: {args.folder}")
            sys.exit(1)

        results = run_batch(
            folder_path=args.folder,
            beam_size=args.beam_size,
            max_steps=args.max_steps,
            api_base=args.api_base,
            output_dir=args.output,
            verbose=verbose
        )

        # Exit code based on success rate
        success_rate = sum(1 for r in results.values() if r.success) / max(len(results), 1)
        sys.exit(0 if success_rate > 0.5 else 1)


if __name__ == '__main__':
    main()
