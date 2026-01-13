"""
Task 87 Success Criteria Verifier
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


def task_87_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Canal Restoration - collect 6x logs, 8x ironore, 4x rawshrimp, craft 2x pickaxe."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and tools
    logs = count_item_in_inventories(inventories, 'logs')
    ironore = count_item_in_inventories(inventories, 'ironore')
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')

    has_logs = logs >= 6
    has_ironore = ironore >= 8
    has_shrimp = rawshrimp >= 4
    has_pickaxe = pickaxe >= 2

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_logs and has_ironore and has_shrimp and has_pickaxe and alive
    msg = f"Logs: {logs}/6, Ironore: {ironore}/8, Shrimp: {rawshrimp}/4, Pickaxe: {pickaxe}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 87."""
    return task_87_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_87_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
