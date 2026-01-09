"""
Task 91 Success Criteria Verifier
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


def task_91_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Royal Tournament - 3 challenges."""
    inventories = get_final_inventories(traj_json)
    
    legendary_items = ['heavysword', 'goldring', 'icestaff', 'silverring', 'axe', 'emeraldpendant']
    legendary_count = sum(1 for item in legendary_items if has_item_in_any_inventory(inventories, item))
    
    food_items = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, item) for item in food_items)
    
    alive = check_agents_alive(traj_json)
    success = alive and legendary_count >= 5 and food_count >= 20
    msg = f"Alive: {alive}, Legendary items: {legendary_count}/5, Food: {food_count}/20"
    return (1 if success else 0, msg)


# =============================================================================
# CONSTRUCTION TASKS (41, 43, 74, 76, 81, 84, 87, 89, 90, 93)
# =============================================================================


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 91."""
    return task_91_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_91_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
