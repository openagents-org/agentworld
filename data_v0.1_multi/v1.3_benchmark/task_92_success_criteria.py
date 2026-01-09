"""
Task 92 Success Criteria Verifier
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


def task_92_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Continental Trade Network - multiple production targets."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cookedshrimp = item_counts.get("cookedshrimp", 0)
    jellyfishsmoothie = item_counts.get("jellyfishsmoothie", 0)
    ironbar = item_counts.get("ironbar", 0)
    goldbar = item_counts.get("goldbar", 0)
    goldring = item_counts.get("goldring", 0)
    heavysword = item_counts.get("heavysword", 0) + item_counts.get("sword2", 0)
    axe = item_counts.get("axe", 0)

    shrimp_passed = cookedshrimp >= 20
    smoothie_passed = jellyfishsmoothie >= 8
    iron_passed = ironbar >= 15
    gold_passed = goldbar >= 8
    ring_passed = goldring >= 3
    sword_passed = heavysword >= 2
    axe_passed = axe >= 2

    passed = (shrimp_passed and smoothie_passed and iron_passed and
              gold_passed and ring_passed and sword_passed and axe_passed)
    msg = f"Shrimp: {cookedshrimp}/20, Smoothie: {jellyfishsmoothie}/8, Iron: {ironbar}/15, Gold: {goldbar}/8, Rings: {goldring}/3, Swords: {heavysword}/2, Axes: {axe}/2"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 92."""
    return task_92_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_92_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
