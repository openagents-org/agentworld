"""
Task 51 Success Criteria Verifier
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


def task_51_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Survival Challenge - craft 1x woodenbow, 1x axe, collect 5x rawshrimp, 4x logs."""
    inventories = get_final_inventories(traj_json)

    # Check for required items
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')
    axe = count_item_in_inventories(inventories, 'axe')
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    logs = count_item_in_inventories(inventories, 'logs')

    has_bow = woodenbow >= 1
    has_axe = axe >= 1
    has_shrimp = rawshrimp >= 5
    has_logs = logs >= 4

    # Check all agents alive
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    passed = has_bow and has_axe and has_shrimp and has_logs and all_alive
    msg = f"Bow: {woodenbow}/1, Axe: {axe}/1, Shrimp: {rawshrimp}/5, Logs: {logs}/4, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 51."""
    return task_51_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_51_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
