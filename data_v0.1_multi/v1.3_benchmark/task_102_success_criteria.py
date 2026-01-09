"""
Task 102 Success Criteria Verifier
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


def task_102_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Harmony Ritual - 5 fire staffs, 5 ice staffs, 5 nature staffs."""
    inventories = get_final_inventories(traj_json)

    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    firestaff = item_counts.get("firestaff", 0)
    icestaff = item_counts.get("icestaff", 0)
    naturestaff = item_counts.get("naturestaff", 0)

    fire_passed = firestaff >= 5
    ice_passed = icestaff >= 5
    nature_passed = naturestaff >= 5

    passed = fire_passed and ice_passed and nature_passed
    msg = f"Fire staffs: {firestaff}/5, Ice staffs: {icestaff}/5, Nature staffs: {naturestaff}/5"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 102."""
    return task_102_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_102_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
