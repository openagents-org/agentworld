"""
Task 03 Success Criteria Verifier
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


def task_03_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Silver Ring Forging."""
    inventories = get_final_inventories(traj_json)
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    msg = f"Silver ring: {silverring}"
    return (1 if silverring else 0, msg)


def task_03_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    silverring = count_item_in_inventories(inventories, 'silverring')
    msg = f"Silver rings: {silverring}/2"
    return (1 if silverring >= 2 else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 03."""
    return task_03_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_03_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
