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
    """Relief Convoy.
    YAML criteria:
    - Team inventory contains 6x cookedshrimp
    - Team inventory contains 2x pickaxe
    - Team inventory contains at least 8x logs
    """
    inventories = get_final_inventories(traj_json)

    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')
    logs = count_item_in_inventories(inventories, 'logs')

    shrimp_ok = cookedshrimp >= 6
    pick_ok = pickaxe >= 2
    logs_ok = logs >= 8

    success = shrimp_ok and pick_ok and logs_ok
    msg = f"Cookedshrimp: {cookedshrimp}/6, Pickaxe: {pickaxe}/2, Logs: {logs}/8"
    return (1 if success else 0, msg)


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
