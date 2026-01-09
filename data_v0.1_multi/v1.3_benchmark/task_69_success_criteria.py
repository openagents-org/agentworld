"""
Task 69 Success Criteria Verifier
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


def task_69_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Legendary Equipment Forge."""
    inventories = get_final_inventories(traj_json)
    legendary = ['goldensword', 'goldenbow', 'goldring', 'lightningstaff', 'firestaff']
    legendary_count = sum(1 for l in legendary if has_item_in_any_inventory(inventories, l))
    success = legendary_count >= 2
    msg = f"Legendary items: {legendary_count}/2"
    return (1 if success else 0, msg)


def task_69_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    golden_keys = ["goldensword", "goldenbow", "goldring", "goldenring", "goldenboots"]
    staff_keys = ["lightningstaff", "firestaff", "icestaff", "naturestaff", "magicstaff"]
    elite_weapon_keys = ["heavysword", "sword2", "axe", "goldenbow", "bow", "pickaxe"]
    golden_count = sum(count_item_in_inventories(inventories, k) for k in golden_keys)
    staff_count = sum(count_item_in_inventories(inventories, k) for k in staff_keys)
    elite_count = sum(count_item_in_inventories(inventories, k) for k in elite_weapon_keys)
    success = golden_count >= 5 and staff_count >= 4 and elite_count >= 6
    msg = (f"Golden items: {golden_count}/5, Staffs: {staff_count}/4, "
           f"Elite weapons/armor: {elite_count}/6")
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 69."""
    return task_69_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_69_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
