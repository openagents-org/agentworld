"""
Task 37 Success Criteria Verifier
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


def task_37_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Survival Gathering - collect 5x blueberry, 3x corn, 4x logs."""
    inventories = get_final_inventories(traj_json)

    # Check for resources
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    corn = count_item_in_inventories(inventories, 'corn')
    logs = count_item_in_inventories(inventories, 'logs')

    has_blueberry = blueberry >= 5
    has_corn = corn >= 3
    has_logs = logs >= 4

    # Check all agents alive
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    passed = has_blueberry and has_corn and has_logs and all_alive
    msg = f"Blueberry: {blueberry}/5, Corn: {corn}/3, Logs: {logs}/4, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 37."""
    return task_37_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_37_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
