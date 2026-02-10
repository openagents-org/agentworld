"""
Task 71 Success Criteria Verifier
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


def task_71_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Region Supply Network.
    YAML criteria:
    - Team inventory contains at least 6x logs
    - Team inventory contains 2x axe
    - Team inventory contains 1x woodenbow
    - Team inventory contains 1x pickaxe
    - Team inventory contains 1x sword2 (heavy sword)
    """
    inventories = get_final_inventories(traj_json)

    logs = count_item_in_inventories(inventories, 'logs')
    axe = count_item_in_inventories(inventories, 'axe')
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')
    sword2 = count_item_in_inventories(inventories, 'sword2') + count_item_in_inventories(inventories, 'heavysword')

    logs_ok = logs >= 6
    axe_ok = axe >= 2
    bow_ok = woodenbow >= 1
    pickaxe_ok = pickaxe >= 1
    sword_ok = sword2 >= 1

    success = logs_ok and axe_ok and bow_ok and pickaxe_ok and sword_ok
    msg = f"Logs: {logs}/6, Axe: {axe}/2, Woodenbow: {woodenbow}/1, Pickaxe: {pickaxe}/1, Sword2: {sword2}/1"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 71."""
    return task_71_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_71_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
