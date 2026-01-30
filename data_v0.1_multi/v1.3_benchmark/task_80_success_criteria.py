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
    """Festival Preparation - 4x cookedshrimp, 3x jellyfishsmoothie, 2x silverring."""
    inventories = get_final_inventories(traj_json)

    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    jellyfishsmoothie = count_item_in_inventories(inventories, 'jellyfishsmoothie')
    silverring = count_item_in_inventories(inventories, 'silverring')

    shrimp_passed = cookedshrimp >= 4
    smoothie_passed = jellyfishsmoothie >= 3
    ring_passed = silverring >= 2

    passed = shrimp_passed and smoothie_passed and ring_passed
    msg = f"Cooked Shrimp: {cookedshrimp}/4, Jellyfish Smoothie: {jellyfishsmoothie}/3, Silver Ring: {silverring}/2"
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
