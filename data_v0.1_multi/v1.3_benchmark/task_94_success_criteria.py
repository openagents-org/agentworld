"""
Task 94 Success Criteria Verifier
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


def task_94_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Maritime Trading Empire - 30+ seafood, 20+ tools, 30+ luxury, 80+ total."""
    inventories = get_final_inventories(traj_json)
    
    seafood_keys = ["rawshrimp", "shrimp", "jellyfish", "crab", "rawtuna", "tuna", "fish"]
    tool_weapon_keys = ["axe", "sword", "pickaxe", "bow", "arrow", "heavysword", "sword1", "sword2"]
    luxury_keys = ["ring", "goldring", "silverring", "pendant", "staff", "cookedshrimp",
                   "cookedtuna", "jellyfishsmoothie", "emerald", "ruby", "bead"]
    starting_items = ["flask", "apple", "leatherarmor", "leatherboots"]

    seafood_count = 0
    tool_count = 0
    luxury_count = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in starting_items:
                continue
            if any(sf in k for sf in seafood_keys):
                seafood_count += x
            elif any(tw in k for tw in tool_weapon_keys):
                tool_count += x
            elif any(lx in k for lx in luxury_keys):
                luxury_count += x

    total = seafood_count + tool_count + luxury_count

    seafood_passed = seafood_count >= 30
    tool_passed = tool_count >= 20
    luxury_passed = luxury_count >= 30
    total_passed = total >= 80

    passed = seafood_passed and tool_passed and luxury_passed and total_passed
    msg = f"Seafood: {seafood_count}/30, Tools: {tool_count}/20, Luxury: {luxury_count}/30, Total: {total}/80"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 94."""
    return task_94_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_94_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
