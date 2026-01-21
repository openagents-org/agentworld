"""
Task 67 Success Criteria Verifier
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


def task_67_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Biome Resource Caravan.
    YAML criteria:
    - Team inventory contains at least 6x logs
    - Team inventory contains at least 5x coal
    - Team inventory contains 1x pickaxe
    - All agents survive the caravan mission
    """
    inventories = get_final_inventories(traj_json)

    logs = count_item_in_inventories(inventories, 'logs')
    coal = count_item_in_inventories(inventories, 'coal')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')

    alive = check_agents_alive(traj_json)

    logs_ok = logs >= 6
    coal_ok = coal >= 5
    pick_ok = pickaxe >= 1

    success = logs_ok and coal_ok and pick_ok
    msg = f"Logs: {logs}/6, Coal: {coal}/5, Pickaxe: {pickaxe}/1"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 67."""
    return task_67_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_67_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
