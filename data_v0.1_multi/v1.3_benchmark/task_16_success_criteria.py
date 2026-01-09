"""
Task 16 Success Criteria Verifier
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


def task_16_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Resource Protection Mission - protect collectors while gathering resources."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_agents_alive(traj_json)
    
    success = logs >= 5 and blueberry >= 3 and alive
    msg = f"Logs: {logs}/5, Blueberry: {blueberry}/3, All alive: {alive}"
    return (1 if success else 0, msg)


def task_16_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_agents_alive(traj_json)
    success = logs >= 7 and blueberry >= 4 and alive
    msg = f"Logs: {logs}/7, Blueberry: {blueberry}/4, All alive: {alive}"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 16."""
    return task_16_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_16_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
