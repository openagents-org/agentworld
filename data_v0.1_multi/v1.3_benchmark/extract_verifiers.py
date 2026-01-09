#!/usr/bin/env python3
"""
Script to extract task verifiers from task_verifier.py into individual files.
"""

import re
import os

# Source file
SOURCE_FILE = "/home/ubuntu/works/agentworld/task_verifier.py"
OUTPUT_DIR = "/home/ubuntu/works/agentworld/data_v0.1_multi/v1.3_benchmark"

# Read the source file
with open(SOURCE_FILE, 'r') as f:
    content = f.read()

# Find all task verifier functions
# Pattern matches: def task_XX_verifier(traj_json: Dict) -> Tuple[int, str]:
pattern = r'(def task_(\d+)_verifier(?:_v\d+)?\(traj_json: Dict\) -> Tuple\[int, str\]:.*?)(?=\ndef |\nclass |\Z)'
matches = re.findall(pattern, content, re.DOTALL)

print(f"Found {len(matches)} verifier functions")

# Group by task number
task_verifiers = {}
for func_code, task_num in matches:
    task_num = int(task_num)
    if task_num not in task_verifiers:
        task_verifiers[task_num] = []
    task_verifiers[task_num].append(func_code.strip())

print(f"Grouped into {len(task_verifiers)} tasks")

# Create individual files
for task_num in sorted(task_verifiers.keys()):
    verifiers = task_verifiers[task_num]

    # Generate filename
    filename = f"task_{task_num:02d}_success_criteria.py"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Generate file content
    file_content = f'''"""
Task {task_num:02d} Success Criteria Verifier
Auto-extracted from task_verifier.py
"""

from typing import Dict, Tuple
from verifier_utils import (
    get_final_inventories,
    aggregate_item_counts,
    get_all_inventories,
    count_item_in_inventories,
    has_item_in_any_inventory,
    check_agents_alive,
    get_final_hp,
    get_final_agent_status,
    get_final_agent_hp_simple,
    count_combat_kills,
    count_attack_actions,
    count_crafted_items,
    check_crafted_items,
    count_chat_messages,
    get_agent_items_by_username,
)


'''

    # Add all verifier functions for this task
    for verifier in verifiers:
        file_content += verifier + "\n\n\n"

    # Add main entry point - use base verifier or v1 as default
    func_names = []
    for v in verifiers:
        match = re.search(r'def (task_\d+_verifier(?:_v\d+)?)\(', v)
        if match:
            func_names.append(match.group(1))

    # Prefer base verifier (without _v suffix), then whatever is first
    main_func = None
    for name in func_names:
        if '_v1' not in name and '_v2' not in name:  # base verifier (no version suffix)
            main_func = name
            break
    if not main_func and func_names:
        main_func = func_names[0]

    if main_func:
        file_content += f'''def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task {task_num:02d}."""
    return {main_func}(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python {filename} <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {{success}}")
    print(f"Message: {{msg}}")
'''

    # Write file
    with open(filepath, 'w') as f:
        f.write(file_content)

    print(f"Created: {filename}")

print(f"\nDone! Created {len(task_verifiers)} verifier files in {OUTPUT_DIR}")
