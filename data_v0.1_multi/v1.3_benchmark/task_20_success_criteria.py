"""
Task 20 Success Criteria Verifier
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


def task_20_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Orchard Protection - berry_picker needs 6+ blueberry, pond_fisher needs 3+ rawtuna."""
    agent_items = get_agent_items_by_username(traj_json)

    berry_picker_items = {}
    for username, items in agent_items.items():
        if "berry_picker" in username.lower():
            berry_picker_items = items
            break

    pond_fisher_items = {}
    for username, items in agent_items.items():
        if "pond_fisher" in username.lower():
            pond_fisher_items = items
            break

    blueberry = berry_picker_items.get("blueberry", 0)
    rawtuna = pond_fisher_items.get("rawtuna", 0)

    berry_passed = blueberry >= 6
    tuna_passed = rawtuna >= 3
    passed = berry_passed and tuna_passed

    msg = f"blueberry: {blueberry}/6, rawtuna: {rawtuna}/3"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 20."""
    return task_20_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_20_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
