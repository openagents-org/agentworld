"""
Task 92 Success Criteria Verifier
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


def task_92_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Trade Network - collect 8x logs, 6x ironore, 4x rawshrimp, craft 2x Gold Ring."""
    inventories = get_final_inventories(traj_json)

    # Count resources
    logs = count_item_in_inventories(inventories, 'logs')
    ironore = count_item_in_inventories(inventories, 'ironore')
    ironbar = count_item_in_inventories(inventories, 'ironbar')  # smelted iron counts too
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')  # cooked shrimp counts too
    goldring = count_item_in_inventories(inventories, 'goldring')

    # Iron ore or smelted bars count
    iron_total = ironore + ironbar
    # Raw or cooked shrimp count
    shrimp_total = rawshrimp + cookedshrimp

    has_logs = logs >= 8
    has_iron = iron_total >= 6
    has_shrimp = shrimp_total >= 4
    has_rings = goldring >= 2

    alive = check_agents_alive(traj_json)

    passed = has_logs and has_iron and has_shrimp and has_rings and alive
    msg = f"Logs: {logs}/8, Iron(ore+bar): {iron_total}/6, Shrimp(raw+cooked): {shrimp_total}/4, Gold Ring: {goldring}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 92."""
    return task_92_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_92_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
