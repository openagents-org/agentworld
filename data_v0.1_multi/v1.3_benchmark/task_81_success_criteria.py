"""
Task 81 Success Criteria Verifier
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


def task_81_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Grid - collect 8x icelogs, 6x logs, craft 1x lightningstaff, 1x firestaff."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and staffs
    icelogs = count_item_in_inventories(inventories, 'icelogs')
    logs = count_item_in_inventories(inventories, 'logs')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')

    has_icelogs = icelogs >= 8
    has_logs = logs >= 6
    has_lightning = lightningstaff >= 1
    has_fire = firestaff >= 1

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_icelogs and has_logs and has_lightning and has_fire and alive
    msg = f"Icelogs: {icelogs}/8, Logs: {logs}/6, Lightning: {lightningstaff}/1, Fire: {firestaff}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 81."""
    return task_81_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_81_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
