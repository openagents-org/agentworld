"""
Task 89 Success Criteria Verifier
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


def task_89_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Beacon Calibration - collect 8x logs, 6x icelogs, craft 1x berylpendant, 1x lightningstaff."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and items
    logs = count_item_in_inventories(inventories, 'logs')
    icelogs = count_item_in_inventories(inventories, 'icelogs')
    berylpendant = count_item_in_inventories(inventories, 'berylpendant')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')

    has_logs = logs >= 8
    has_icelogs = icelogs >= 6
    has_pendant = berylpendant >= 1
    has_staff = lightningstaff >= 1

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_logs and has_icelogs and has_pendant and has_staff and alive
    msg = f"Logs: {logs}/8, Icelogs: {icelogs}/6, Pendant: {berylpendant}/1, Staff: {lightningstaff}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 89."""
    return task_89_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_89_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
