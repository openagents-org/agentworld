"""
Task 56 Success Criteria Verifier
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


def task_56_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Cross-Region Trading Network - 3x goldring, 2x lightningstaff, 1x heavysword."""
    inventories = get_final_inventories(traj_json)
    
    goldring = count_item_in_inventories(inventories, 'goldring')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')

    goldring_passed = goldring >= 3
    staff_passed = lightningstaff >= 2
    sword_passed = heavysword >= 1

    passed = goldring_passed and staff_passed and sword_passed
    msg = f"Gold Rings: {goldring}/3, Lightning Staffs: {lightningstaff}/2, Heavy Swords: {heavysword}/1"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 56."""
    return task_56_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_56_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
