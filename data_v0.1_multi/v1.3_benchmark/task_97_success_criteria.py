"""
Task 97 Success Criteria Verifier
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


def task_97_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Agricultural Empire."""
    inventories = get_final_inventories(traj_json)
    crops = ['corn', 'tomato', 'blueberry', 'apple']
    crop_count = sum(count_item_in_inventories(inventories, c) for c in crops)
    success = crop_count >= 30
    msg = f"Crops: {crop_count}/30"
    return (1 if success else 0, msg)


# =============================================================================
# EXPLORATION TASKS (100, 21, 23, 24, 33, 46, 48, 53, 57, 60, 70, 73, 79, 95)
# =============================================================================


def task_97_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    food_keys = ["corn", "tomato", "blueberry", "apple", "rawshrimp", "rawtuna",
                 "fish", "cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                 "cookedmeat", "jellyfishsmoothie", "stew", "stew2"]
    total_food = sum(count_item_in_inventories(inventories, k) for k in food_keys)
    success = total_food >= 150
    msg = f"Food items: {total_food}/150"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 97."""
    return task_97_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_97_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
