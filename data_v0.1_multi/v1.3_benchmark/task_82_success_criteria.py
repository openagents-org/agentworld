"""
Task 82 Success Criteria Verifier
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


def task_82_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Evacuation - collect 8x logs, 6x ironore, craft 2x axe."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and tools
    logs = count_item_in_inventories(inventories, 'logs')
    ironore = count_item_in_inventories(inventories, 'ironore')
    axe = count_item_in_inventories(inventories, 'axe')

    has_logs = logs >= 8
    has_ironore = ironore >= 6
    has_axes = axe >= 2

    # Check all agents alive
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp['current'] > 0 for hp in agent_hp.values()) if agent_hp else False

    passed = has_logs and has_ironore and has_axes and all_alive
    msg = f"Logs: {logs}/8, Ironore: {ironore}/6, Axe: {axe}/2, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 82."""
    return task_82_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_82_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
