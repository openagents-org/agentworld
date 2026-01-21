"""
Task 40 Success Criteria Verifier
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


def task_40_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Healing Supplies - collect 4x cookedshrimp."""
    inventories = get_final_inventories(traj_json)

    # Check for cooked shrimp
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    return (1 if cookedshrimp >= 4 else 0, f"Cooked shrimp: {cookedshrimp}/4")


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 40."""
    return task_40_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_40_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
