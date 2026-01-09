"""
Task 17 Success Criteria Verifier
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


def task_17_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forest Gathering - palm_logger needs 4+ palmlogs, peach_forager needs 5+ peach."""
    agent_items = get_agent_items_by_username(traj_json)
    
    palm_logger_items = {}
    for username, items in agent_items.items():
        if "palm_logger" in username.lower():
            palm_logger_items = items
            break

    peach_forager_items = {}
    for username, items in agent_items.items():
        if "peach_forager" in username.lower():
            peach_forager_items = items
            break

    palmlogs = palm_logger_items.get("palmlogs", 0)
    peach = peach_forager_items.get("peach", 0)

    palm_passed = palmlogs >= 4
    peach_passed = peach >= 5
    passed = palm_passed and peach_passed

    msg = f"palmlogs: {palmlogs}/4, peach: {peach}/5"
    return (1 if passed else 0, msg)


def task_17_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    agent_items = get_agent_items_by_username(traj_json)
    palm_logger_items = {}
    for username, items in agent_items.items():
        if "palm_logger" in username.lower():
            palm_logger_items = items
            break
    peach_forager_items = {}
    for username, items in agent_items.items():
        if "peach_forager" in username.lower():
            peach_forager_items = items
            break
    palmlogs = palm_logger_items.get("palmlogs", 0)
    peach = peach_forager_items.get("peach", 0)
    palm_passed = palmlogs >= 6
    peach_passed = peach >= 8
    msg = f"palmlogs: {palmlogs}/6, peach: {peach}/8"
    return (1 if palm_passed and peach_passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 17."""
    return task_17_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_17_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
