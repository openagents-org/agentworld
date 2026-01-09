"""
Task 18 Success Criteria Verifier
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


def task_18_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Coastal Harvest - shrimp_fisher needs 6+ rawshrimp, ice_logger needs 3+ icelogs."""
    agent_items = get_agent_items_by_username(traj_json)

    shrimp_fisher_items = {}
    for username, items in agent_items.items():
        if "shrimp_fisher" in username.lower():
            shrimp_fisher_items = items
            break

    ice_logger_items = {}
    for username, items in agent_items.items():
        if "ice_logger" in username.lower():
            ice_logger_items = items
            break

    rawshrimp = shrimp_fisher_items.get("rawshrimp", 0)
    icelogs = ice_logger_items.get("icelogs", 0)

    shrimp_passed = rawshrimp >= 6
    ice_passed = icelogs >= 3
    passed = shrimp_passed and ice_passed

    msg = f"rawshrimp: {rawshrimp}/6, icelogs: {icelogs}/3"
    return (1 if passed else 0, msg)


def task_18_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    agent_items = get_agent_items_by_username(traj_json)
    shrimp_fisher_items = {}
    for username, items in agent_items.items():
        if "shrimp_fisher" in username.lower():
            shrimp_fisher_items = items
            break
    ice_logger_items = {}
    for username, items in agent_items.items():
        if "ice_logger" in username.lower():
            ice_logger_items = items
            break
    rawshrimp = shrimp_fisher_items.get("rawshrimp", 0)
    icelogs = ice_logger_items.get("icelogs", 0)
    shrimp_passed = rawshrimp >= 9
    ice_passed = icelogs >= 4
    msg = f"rawshrimp: {rawshrimp}/9, icelogs: {icelogs}/4"
    return (1 if shrimp_passed and ice_passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 18."""
    return task_18_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_18_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
