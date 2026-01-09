"""
Task 78 Success Criteria Verifier
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


def task_78_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Transcontinental Trading Network - craft 5 specific items."""
    inventories = get_final_inventories(traj_json)
    
    all_items = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            all_items[k] = all_items.get(k, 0) + x

    golden_bow = all_items.get("goldenbow", 0)
    beryl_pendant = all_items.get("berylpendant", 0) + all_items.get("pendant", 0)
    golden_ring = all_items.get("goldring", 0) + all_items.get("goldenring", 0)
    silver_ring = all_items.get("silverring", 0)
    magic_staff = all_items.get("magicstaff", 0)

    bow_passed = golden_bow >= 1
    pendant_passed = beryl_pendant >= 1
    goldring_passed = golden_ring >= 1
    silverring_passed = silver_ring >= 1
    staff_passed = magic_staff >= 1

    passed = bow_passed and pendant_passed and goldring_passed and silverring_passed and staff_passed
    msg = f"Golden Bow: {golden_bow}/1, Beryl Pendant: {beryl_pendant}/1, Golden Ring: {golden_ring}/1, Silver Ring: {silver_ring}/1, Magic Staff: {magic_staff}/1"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 78."""
    return task_78_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_78_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
