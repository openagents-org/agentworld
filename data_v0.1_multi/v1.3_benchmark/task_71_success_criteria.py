"""
Task 71 Success Criteria Verifier
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


def task_71_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Region Supply Network - 40+ iron bars, 20+ gold bars, 10+ weapons, 7+ rings."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    iron_bars = item_counts.get("ironbar", 0)
    gold_bars = item_counts.get("goldbar", 0)
    weapons = (item_counts.get("sword", 0) + item_counts.get("sword1", 0) +
               item_counts.get("sword2", 0) + item_counts.get("heavysword", 0) +
               item_counts.get("axe", 0) + item_counts.get("bow", 0))
    rings = (item_counts.get("goldring", 0) + item_counts.get("ring", 0) +
             item_counts.get("silverring", 0))

    iron_passed = iron_bars >= 40
    gold_passed = gold_bars >= 20
    weapons_passed = weapons >= 10
    rings_passed = rings >= 7

    passed = iron_passed and gold_passed and weapons_passed and rings_passed
    msg = f"Iron bars: {iron_bars}/40, Gold bars: {gold_bars}/20, Weapons: {weapons}/10, Rings: {rings}/7"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 71."""
    return task_71_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_71_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
