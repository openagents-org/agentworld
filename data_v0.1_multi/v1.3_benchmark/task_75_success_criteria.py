"""
Task 75 Success Criteria Verifier
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


def task_75_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Continental Relief Convoy - 30+ iron bars, 30+ cooked shrimp, 60+ arrows, all HP > 25%."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    ironbar = item_counts.get("ironbar", 0)
    cookedshrimp = item_counts.get("cookedshrimp", 0)
    arrow = item_counts.get("arrow", 0)

    agent_hp = get_final_agent_status(traj_json)
    all_healthy = True
    for agent, hp_data in agent_hp.items():
        percent = (hp_data['current'] / hp_data['max'] * 100) if hp_data['max'] > 0 else 0
        if percent <= 25:
            all_healthy = False

    ironbar_passed = ironbar >= 30
    shrimp_passed = cookedshrimp >= 30
    arrow_passed = arrow >= 60
    hp_passed = all_healthy

    passed = ironbar_passed and shrimp_passed and arrow_passed and hp_passed
    msg = f"Iron bars: {ironbar}/30, Cooked shrimp: {cookedshrimp}/30, Arrows: {arrow}/60, HP>25%: {hp_passed}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 75."""
    return task_75_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_75_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
