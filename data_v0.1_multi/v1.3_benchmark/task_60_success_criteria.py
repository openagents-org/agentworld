"""
Task 60 Success Criteria Verifier
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


def task_60_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mining Operation - smelt 6x ironbar, craft 1x Pickaxe and 1x Silver Ring."""
    inventories = get_final_inventories(traj_json)
    
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')
    silverring = count_item_in_inventories(inventories, 'silverring')
    
    # Note: ironbars get consumed when crafting, so check for final products
    # Pickaxe requires 5 ironbar, silver ring requires 2 ironbar
    # So we check if they have the products OR enough ironbar
    has_pickaxe = pickaxe >= 1
    has_ring = silverring >= 1
    
    # Check all agents alive
    alive = check_agents_alive(traj_json)
    
    passed = has_pickaxe and has_ring and alive
    msg = f"Pickaxe: {pickaxe}/1, Silver Ring: {silverring}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def task_60_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    ore_keys = ["ironore", "goldore", "coal", "copperore", "tinore"]
    bar_keys = ["ironbar", "goldbar", "bronzebar", "silverbar", "steelbar"]
    product_keys = ["heavysword", "axe", "goldring", "silverring", "pickaxe", "sword", "bow"]
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ore_keys)
    bar_count = sum(count_item_in_inventories(inventories, b) for b in bar_keys)
    product_count = sum(count_item_in_inventories(inventories, p) for p in product_keys)
    success = ore_count >= 80 and bar_count >= 60 and product_count >= 10
    msg = f"Ores: {ore_count}/80, Bars: {bar_count}/60, Products: {product_count}/10"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 60."""
    return task_60_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_60_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
