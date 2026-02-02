"""
Task 100 Success Criteria Verifier
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


def task_100_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Resource Survey - collect 8x logs, 8x ironore, 6x icelogs, 4x rawshrimp from different regions."""
    inventories = get_final_inventories(traj_json)

    # Count resources
    logs = count_item_in_inventories(inventories, 'logs')
    ironore = count_item_in_inventories(inventories, 'ironore')
    ironbar = count_item_in_inventories(inventories, 'ironbar')  # smelted iron counts too
    icelogs = count_item_in_inventories(inventories, 'icelogs')
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')  # cooked shrimp counts too

    # Iron ore or smelted bars count
    iron_total = ironore + ironbar
    # Raw or cooked shrimp count
    shrimp_total = rawshrimp + cookedshrimp

    has_logs = logs >= 8
    has_iron = iron_total >= 8
    has_icelogs = icelogs >= 6
    has_shrimp = shrimp_total >= 4

    alive = check_agents_alive(traj_json)

    passed = has_logs and has_iron and has_icelogs and has_shrimp and alive
    msg = f"Logs: {logs}/8, Iron(ore+bar): {iron_total}/8, Ice Logs: {icelogs}/6, Shrimp(raw+cooked): {shrimp_total}/4, All alive: {alive}"
    return (1 if passed else 0, msg)


# =============================================================================
# SPECIALIZED TASKS FROM verify/ FOLDER
# =============================================================================


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 100."""
    return task_100_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_100_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
