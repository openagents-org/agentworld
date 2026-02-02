"""
Task 75 Success Criteria Verifier
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


def task_75_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Relief Convoy - 6+ cooked shrimp, 2+ pickaxe, 8+ logs."""
    inventories = get_final_inventories(traj_json)

    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cookedshrimp = item_counts.get("cookedshrimp", 0)
    pickaxe = item_counts.get("pickaxe", 0)
    logs = item_counts.get("logs", 0)

    shrimp_passed = cookedshrimp >= 6
    pickaxe_passed = pickaxe >= 2
    logs_passed = logs >= 8

    passed = shrimp_passed and pickaxe_passed and logs_passed
    msg = f"Cooked shrimp: {cookedshrimp}/6, Pickaxe: {pickaxe}/2, Logs: {logs}/8"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 75."""
    return task_75_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_75_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
