"""
Task 85 Success Criteria Verifier
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


def task_85_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ice Convoy - collect 10x icelogs, 4x rawshrimp, craft 1x icestaff."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and staffs
    icelogs = count_item_in_inventories(inventories, 'icelogs')
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    icestaff = count_item_in_inventories(inventories, 'icestaff')

    has_icelogs = icelogs >= 10
    has_shrimp = rawshrimp >= 4
    has_icestaff = icestaff >= 1

    passed = has_icelogs and has_shrimp and has_icestaff
    msg = f"Icelogs: {icelogs}/10, Shrimp: {rawshrimp}/4, Icestaff: {icestaff}/1"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 85."""
    return task_85_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_85_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
