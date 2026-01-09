"""
Task 59 Success Criteria Verifier
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


def task_59_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Merchant Guild - 4x golden items, 3x staffs, 2x specialty weapons."""
    inventories = get_final_inventories(traj_json)
    
    golden_items = ["goldensword", "goldenbow", "goldenboots", "goldring", "goldenring"]
    elemental_staffs = ["lightningstaff", "firestaff", "icestaff"]
    specialty_weapons = ["pickaxe", "heavysword", "sword2"]

    golden_count = 0
    staff_count = 0
    weapon_count = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)

            if k in golden_items:
                golden_count += x
            elif k in elemental_staffs:
                staff_count += x
            elif k in specialty_weapons:
                weapon_count += x

    golden_passed = golden_count >= 4
    staff_passed = staff_count >= 3
    weapon_passed = weapon_count >= 2

    passed = golden_passed and staff_passed and weapon_passed
    msg = f"Golden items: {golden_count}/4, Staffs: {staff_count}/3, Weapons: {weapon_count}/2"
    return (1 if passed else 0, msg)


def task_59_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    golden_items = ["goldensword", "goldenbow", "goldenboots", "goldring", "goldenring"]
    elemental_staffs = ["lightningstaff", "firestaff", "icestaff"]
    specialty_weapons = ["pickaxe", "heavysword", "sword2"]

    golden_count = 0
    staff_count = 0
    weapon_count = 0
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in golden_items:
                golden_count += x
            elif k in elemental_staffs:
                staff_count += x
            elif k in specialty_weapons:
                weapon_count += x

    golden_passed = golden_count >= 5
    staff_passed = staff_count >= 3
    weapon_passed = weapon_count >= 2
    success = golden_passed and staff_passed and weapon_passed
    msg = f"Golden items: {golden_count}/5, Staffs: {staff_count}/3, Weapons: {weapon_count}/2"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 59."""
    return task_59_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_59_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
