"""
Task 98 Success Criteria Verifier
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


def task_98_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mining Conglomerate - 120+ ores, 100+ bars, 20+ products."""
    inventories = get_final_inventories(traj_json)
    
    ore_keys = ["ironore", "goldore", "coal"]
    bar_keys = ["ironbar", "goldbar", "bronzebar", "silverbar", "steelbar"]
    product_keys = ["heavysword", "axe", "goldring", "silverring", "pickaxe", "sword", "dagger"]

    ore_totals = {}
    bar_totals = {}
    product_totals = {}

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in ore_keys:
                ore_totals[k] = ore_totals.get(k, 0) + x
            elif k in bar_keys:
                bar_totals[k] = bar_totals.get(k, 0) + x
            elif k in product_keys:
                product_totals[k] = product_totals.get(k, 0) + x

    total_ores = sum(ore_totals.values())
    total_bars = sum(bar_totals.values())
    total_products = sum(product_totals.values())

    ore_passed = total_ores >= 120
    bar_passed = total_bars >= 100
    product_passed = total_products >= 20

    passed = ore_passed and bar_passed and product_passed
    msg = f"Ores: {total_ores}/120, Bars: {total_bars}/100, Products: {total_products}/20"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 98."""
    return task_98_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_98_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
