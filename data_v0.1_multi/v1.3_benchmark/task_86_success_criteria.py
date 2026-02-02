"""
Task 86 Success Criteria Verifier
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


def task_86_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge Vanguard - 10x ironore, 8x coal, 6x ironbar, 2x heavysword, 1x axe."""
    inventories = get_final_inventories(traj_json)

    ironore = count_item_in_inventories(inventories, 'ironore')
    coal = count_item_in_inventories(inventories, 'coal')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    axe = count_item_in_inventories(inventories, 'axe')

    ironore_passed = ironore >= 10
    coal_passed = coal >= 8
    ironbar_passed = ironbar >= 6
    sword_passed = heavysword >= 2
    axe_passed = axe >= 1

    passed = ironore_passed and coal_passed and ironbar_passed and sword_passed and axe_passed
    msg = f"Ironore: {ironore}/10, Coal: {coal}/8, Ironbar: {ironbar}/6, Heavy Sword: {heavysword}/2, Axe: {axe}/1"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 86."""
    return task_86_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_86_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
