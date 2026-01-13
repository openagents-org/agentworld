"""
Task 41 Success Criteria Verifier
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


def task_41_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Tool Production - craft 1x pickaxe and 1x axe."""
    inventories = get_final_inventories(traj_json)

    # Check for tools
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')
    axe = count_item_in_inventories(inventories, 'axe')

    has_pickaxe = pickaxe >= 1
    has_axe = axe >= 1

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_pickaxe and has_axe and alive
    msg = f"Pickaxe: {pickaxe}/1, Axe: {axe}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 41."""
    return task_41_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_41_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
