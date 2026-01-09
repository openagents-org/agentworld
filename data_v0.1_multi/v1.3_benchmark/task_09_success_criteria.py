"""
Task 09 Success Criteria Verifier
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


def task_09_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Topaz Ring Crafting."""
    inventories = get_final_inventories(traj_json)
    topazring = has_item_in_any_inventory(inventories, 'topazring')
    msg = f"Topaz ring: {topazring}"
    return (1 if topazring else 0, msg)


def task_09_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    topazring = count_item_in_inventories(inventories, 'topazring')
    msg = f"Topaz rings: {topazring}/2"
    return (1 if topazring >= 2 else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 09."""
    return task_09_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_09_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
