"""
Task 99 Success Criteria Verifier
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


def task_99_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Kingdom Festival Celebration - 30+ food, 20+ masterwork, 60+ total."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cooked_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                   "cookedmeat", "jellyfishsmoothie", "stew"]
    masterwork_keys = ["heavysword", "sword2", "axe", "pickaxe", "bow",
                       "goldring", "goldenring", "silverring",
                       "emeraldpendant", "berylpendant", "topazpendant", "pendant",
                       "magicstaff", "lightningstaff"]
    trophy_keys = ["feather", "bead", "lightningbead", "emerald", "ruby", "beryl",
                   "rawmeat", "rawchicken", "rawbeef"]

    cooked_count = sum(item_counts.get(k, 0) for k in cooked_keys)
    masterwork_count = sum(item_counts.get(k, 0) for k in masterwork_keys)
    trophy_count = sum(item_counts.get(k, 0) for k in trophy_keys)
    total_festival = cooked_count + masterwork_count + trophy_count

    food_passed = cooked_count >= 30
    masterwork_passed = masterwork_count >= 20
    total_passed = total_festival >= 60

    passed = food_passed and masterwork_passed and total_passed
    msg = f"Food: {cooked_count}/30, Masterwork: {masterwork_count}/20, Total: {total_festival}/60"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 99."""
    return task_99_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_99_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
