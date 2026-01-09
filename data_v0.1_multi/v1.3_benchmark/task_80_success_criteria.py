"""
Task 80 Success Criteria Verifier
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


def task_80_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Festival Preparation - 10+ food, 4+ rings, 3+ decorations."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cooked_food_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                        "cookedmeat", "jellyfishsmoothie", "stew"]
    cooked_food = sum(item_counts.get(k, 0) for k in cooked_food_keys)

    silver_rings = item_counts.get("silverring", 0)
    golden_rings = item_counts.get("goldring", 0) + item_counts.get("goldenring", 0)
    total_rings = silver_rings + golden_rings

    pendant_keys = ["berylpendant", "topazpendant", "emeraldpendant", "pendant"]
    pendants = sum(item_counts.get(k, 0) for k in pendant_keys)
    staffs = item_counts.get("magicstaff", 0) + item_counts.get("staff", 0) + item_counts.get("lightningstaff", 0)
    decorations = pendants + staffs

    food_passed = cooked_food >= 10
    rings_passed = total_rings >= 4
    decor_passed = decorations >= 3

    passed = food_passed and rings_passed and decor_passed
    msg = f"Food: {cooked_food}/10, Rings: {total_rings}/4, Decorations: {decorations}/3"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 80."""
    return task_80_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_80_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
