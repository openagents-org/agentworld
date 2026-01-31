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
    """Legendary Equipment Forge.
    YAML criteria:
    - Golden Sword, Golden Bow, Golden Boots (3 golden items)
    - 2 Gold Rings
    - 4 magical staffs (lightning, fire, ice, nature)
    - 6 elite weapons (2 swords, 2 pickaxes, 2 axes)
    - Total 15 legendary items created
    """
    inventories = get_final_inventories(traj_json)

    # Golden items
    goldensword = count_item_in_inventories(inventories, 'goldensword')
    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    goldenboots = count_item_in_inventories(inventories, 'goldenboots')
    goldring = count_item_in_inventories(inventories, 'goldring')

    # Staffs
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')
    icestaff = count_item_in_inventories(inventories, 'icestaff')
    naturestaff = count_item_in_inventories(inventories, 'naturestaff')
    total_staffs = lightningstaff + firestaff + icestaff + naturestaff

    # Elite weapons
    sword2 = count_item_in_inventories(inventories, 'sword2') + count_item_in_inventories(inventories, 'heavysword')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')
    axe = count_item_in_inventories(inventories, 'axe')

    total_legendary = goldensword + goldenbow + goldenboots + goldring + total_staffs + sword2 + pickaxe + axe

    gs_ok = goldensword >= 1
    gb_ok = goldenbow >= 1
    gboot_ok = goldenboots >= 1
    ring_ok = goldring >= 2
    staff_ok = total_staffs >= 4
    sword_ok = sword2 >= 2
    pick_ok = pickaxe >= 2
    axe_ok = axe >= 2
    total_ok = total_legendary >= 15

    success = gs_ok and gb_ok and gboot_ok and ring_ok and staff_ok and sword_ok and pick_ok and axe_ok and total_ok
    msg = (f"GoldenSword: {goldensword}/1, GoldenBow: {goldenbow}/1, GoldenBoots: {goldenboots}/1, "
           f"GoldRing: {goldring}/2, Staffs: {total_staffs}/4, Sword2: {sword2}/2, "
           f"Pickaxe: {pickaxe}/2, Axe: {axe}/2, Total: {total_legendary}/15")
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
