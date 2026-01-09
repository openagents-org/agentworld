"""
Task 83 Success Criteria Verifier
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


def task_83_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Relay Ritual - craft all 4 elemental cores."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    berylpendant = item_counts.get("berylpendant", 0)
    goldring = item_counts.get("goldring", 0) + item_counts.get("goldenring", 0)
    cookedtuna = item_counts.get("cookedtuna", 0)
    lightningstaff = item_counts.get("lightningstaff", 0)

    earth_passed = berylpendant >= 1
    flame_passed = goldring >= 1
    tide_passed = cookedtuna >= 1
    gale_passed = lightningstaff >= 1

    passed = earth_passed and flame_passed and tide_passed and gale_passed
    msg = f"Earth(berylpendant): {berylpendant}/1, Flame(goldring): {goldring}/1, Tide(cookedtuna): {cookedtuna}/1, Gale(lightningstaff): {lightningstaff}/1"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 83."""
    return task_83_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_83_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
