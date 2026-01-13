"""
Task 93 Success Criteria Verifier
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


def task_93_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress Construction - collect 8x logs, 8x ironore, 6x coal, craft 2x heavysword, 2x axe."""
    inventories = get_final_inventories(traj_json)

    # Check for resources
    logs = count_item_in_inventories(inventories, 'logs')
    ironore = count_item_in_inventories(inventories, 'ironore')
    coal = count_item_in_inventories(inventories, 'coal')

    # Check for weapons/tools (heavysword can be sword2)
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    axe = count_item_in_inventories(inventories, 'axe')

    has_logs = logs >= 8
    has_ironore = ironore >= 8
    has_coal = coal >= 6
    has_swords = heavysword >= 2
    has_axes = axe >= 2

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_logs and has_ironore and has_coal and has_swords and has_axes and alive
    msg = f"Logs: {logs}/8, Ironore: {ironore}/8, Coal: {coal}/6, Sword: {heavysword}/2, Axe: {axe}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


# =============================================================================
# CRAFTING TASKS
# =============================================================================


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 93."""
    return task_93_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_93_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
