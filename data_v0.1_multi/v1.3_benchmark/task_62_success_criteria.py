"""
Task 62 Success Criteria Verifier
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


def task_62_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Weaponsmith Consortium.
    YAML criteria:
    - Golden Sword (1)
    - Golden Bow (1)
    - Heavy Swords (2)
    - Battle Axes (3)
    - Wooden Bow (1)
    - Pickaxe (1)
    - Total 9 weapons forged
    """
    inventories = get_final_inventories(traj_json)

    goldensword = count_item_in_inventories(inventories, 'goldensword')
    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    axe = count_item_in_inventories(inventories, 'axe')
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')

    total_weapons = goldensword + goldenbow + heavysword + axe + woodenbow + pickaxe

    gs_ok = goldensword >= 1
    gb_ok = goldenbow >= 1
    hs_ok = heavysword >= 2
    axe_ok = axe >= 3
    wb_ok = woodenbow >= 1
    pick_ok = pickaxe >= 1
    total_ok = total_weapons >= 9

    success = gs_ok and gb_ok and hs_ok and axe_ok and wb_ok and pick_ok and total_ok
    msg = f"GoldenSword: {goldensword}/1, GoldenBow: {goldenbow}/1, HeavySword: {heavysword}/2, Axe: {axe}/3, WoodenBow: {woodenbow}/1, Pickaxe: {pickaxe}/1, Total: {total_weapons}/9"
    return (1 if success else 0, msg)


def task_62_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    counts = aggregate_item_counts(inventories)
    sword_keys = ["sword", "sword1", "sword2", "heavysword", "goldensword"]
    axe_keys = ["axe"]
    bow_keys = ["bow", "woodenbow", "goldenbow"]
    pickaxe_keys = ["pickaxe"]
    swords = sum(counts.get(k, 0) for k in sword_keys)
    axes = sum(counts.get(k, 0) for k in axe_keys)
    bows = sum(counts.get(k, 0) for k in bow_keys)
    pickaxes = sum(counts.get(k, 0) for k in pickaxe_keys)
    total = swords + axes + bows + pickaxes
    success = swords >= 5 and axes >= 3 and bows >= 2 and pickaxes >= 1 and total >= 11
    msg = (f"Swords: {swords}/5, Axes: {axes}/3, Bows: {bows}/2, "
           f"Pickaxes: {pickaxes}/1, Total: {total}/11")
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 62."""
    return task_62_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_62_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
