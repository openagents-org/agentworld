"""
Task 68 Success Criteria Verifier
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


def task_68_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Master Toolsmith Consortium."""
    inventories = get_final_inventories(traj_json)
    tools = ['pickaxe', 'axe', 'fishingpole', 'fishingrod']
    tool_count = sum(count_item_in_inventories(inventories, t) for t in tools)
    success = tool_count >= 3
    msg = f"Tools: {tool_count}/3"
    return (1 if success else 0, msg)


def task_68_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    pickaxes = count_item_in_inventories(inventories, 'pickaxe')
    axes = count_item_in_inventories(inventories, 'axe')
    buckets = count_item_in_inventories(inventories, 'bucket')
    specialty_keys = ["fishingpole", "fishingrod", "fishingline", "hammer"]
    specialty = sum(count_item_in_inventories(inventories, k) for k in specialty_keys)
    success = pickaxes >= 8 and axes >= 8 and buckets >= 5 and specialty >= 5
    msg = f"Pickaxes: {pickaxes}/8, Axes: {axes}/8, Buckets: {buckets}/5, Specialty tools: {specialty}/5"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 68."""
    return task_68_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_68_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
