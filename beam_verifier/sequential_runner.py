#!/usr/bin/env python3
"""
Sequential Task Runner

Runs tasks one by one, verifying each before moving to the next.
Uses Claude Agent SDK with claude-sonnet-4-5-20250929 (Sonnet 4.5) for better reasoning.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from .beam_search import run_single_task


def format_action_history(action_history):
    """
    Format action history into a readable structure for JSON output.

    Args:
        action_history: List of step actions from beam search

    Returns:
        List of steps, each containing agent actions
    """
    formatted = []

    for step_num, step_actions in enumerate(action_history, start=1):
        step_data = {
            'step': step_num,
            'actions': []
        }

        for agent_name, action_result in step_actions.items():
            action = action_result.get('action', {})
            success = action_result.get('success', False)
            message = action_result.get('message', '')

            # Format action as a concise string
            action_type = action.get('type', 'unknown')
            action_str = action_type

            if action_type == 'move':
                action_str = f"move(x={action.get('x')}, y={action.get('y')})"
                if action.get('pickupItems'):
                    items = ', '.join(f"{i['key']}x{i['count']}" for i in action.get('pickupItems', []))
                    action_str += f" pickup=[{items}]"
            elif action_type == 'craft':
                action_str = f"craft({action.get('itemKey')}x{action.get('count', 1)})"
            elif action_type == 'collect':
                action_str = f"collect({action.get('resourceKey')})"
            elif action_type == 'transfer':
                action_str = f"transfer({action.get('itemKey')}x{action.get('count', 1)} -> {action.get('targetPlayer')})"
            elif action_type == 'equip':
                action_str = f"equip(slot={action.get('inventoryIndex')})"
            elif action_type == 'drop':
                action_str = f"drop(slot={action.get('inventoryIndex')})"

            step_data['actions'].append({
                'agent': agent_name,
                'action': action_str,
                'success': success,
                'message': message[:100] if message else ''  # Truncate long messages
            })

        formatted.append(step_data)

    return formatted


def run_sequential_verification(
    task_folder: str,
    max_steps: int = 50,
    beam_size: int = 2,
    actions_per_branch: int = 5,
    output_file: str = None,
    start_from: int = 0,
    limit: int = None,
    verbose: bool = True
):
    """
    Run tasks sequentially, one at a time.

    Args:
        task_folder: Path to folder containing task YAML files
        max_steps: Maximum steps per task
        beam_size: Beam search width (branches to keep after pruning)
        actions_per_branch: Number of action sets to propose per branch
        output_file: Optional file to save results
        start_from: Index of task to start from (0-indexed)
        limit: Maximum number of tasks to run
        verbose: Print progress
    """
    # Find all task files
    task_path = Path(task_folder)
    task_files = sorted(task_path.glob("*.yaml"))

    if not task_files:
        print(f"No YAML files found in {task_folder}")
        return

    print(f"Found {len(task_files)} tasks in {task_folder}")
    print(f"Model: {os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')}")
    print(f"Max steps: {max_steps}, Beam size: {beam_size}, Actions/branch: {actions_per_branch}")
    print("=" * 60)

    # Apply start_from and limit
    task_files = task_files[start_from:]
    if limit:
        task_files = task_files[:limit]

    results = []
    success_count = 0

    for i, task_file in enumerate(task_files):
        task_num = start_from + i + 1
        print(f"\n[{task_num}/{start_from + len(task_files)}] Running: {task_file.name}")
        print("-" * 60)

        try:
            result = run_single_task(
                task_path=str(task_file),
                max_steps=max_steps,
                beam_size=beam_size,
                actions_per_branch=actions_per_branch,
                verbose=verbose
            )

            # VerificationResult is a dataclass, use attributes
            success = result.success
            steps = result.steps_taken

            if success:
                success_count += 1
                status = "SUCCESS"
            else:
                status = "FAILED"

            print(f"\n>>> Result: {status} in {steps} steps")

            # Build result entry
            result_entry = {
                'task': task_file.name,
                'success': success,
                'steps': steps,
                'message': result.verifier_message,
                'elapsed_time': result.elapsed_time
            }

            # Include action history for successful tasks (collaboration path)
            if success and result.action_history:
                result_entry['action_history'] = format_action_history(result.action_history)

            results.append(result_entry)

        except Exception as e:
            print(f"\n>>> ERROR: {str(e)}")
            results.append({
                'task': task_file.name,
                'success': False,
                'error': str(e)
            })

        # Save intermediate results
        if output_file:
            with open(output_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'config': {
                        'max_steps': max_steps,
                        'beam_size': beam_size,
                        'model': os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
                    },
                    'summary': {
                        'total': len(results),
                        'success': success_count,
                        'success_rate': success_count / len(results) if results else 0
                    },
                    'results': results
                }, f, indent=2)

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tasks: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"Success rate: {100 * success_count / len(results):.1f}%" if results else "N/A")

    if output_file:
        print(f"\nResults saved to: {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run tasks sequentially with verification"
    )
    parser.add_argument(
        "--folder", "-f",
        type=str,
        default="data_v0.1_multi/v1.3_augmented",
        help="Folder containing task YAML files"
    )
    parser.add_argument(
        "--max-steps", "-s",
        type=int,
        default=50,
        help="Maximum steps per task (default: 50)"
    )
    parser.add_argument(
        "--beam-size", "-b",
        type=int,
        default=2,
        help="Beam search width - branches to keep after pruning (default: 2)"
    )
    parser.add_argument(
        "--actions-per-branch", "-a",
        type=int,
        default=5,
        help="Number of action sets to propose per branch (default: 5)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file for results (JSON)"
    )
    parser.add_argument(
        "--start", "-i",
        type=int,
        default=0,
        help="Start from task index (0-indexed)"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=None,
        help="Limit number of tasks to run"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )

    args = parser.parse_args()

    run_sequential_verification(
        task_folder=args.folder,
        max_steps=args.max_steps,
        beam_size=args.beam_size,
        actions_per_branch=args.actions_per_branch,
        output_file=args.output,
        start_from=args.start,
        limit=args.limit,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
