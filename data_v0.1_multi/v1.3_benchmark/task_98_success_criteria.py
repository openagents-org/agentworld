"""
Task 98 Success Criteria Verifier
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


def task_98_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mining Conglomerate - mine 8x ironore, 6x coal, smelt 6x ironbar, craft 2x Heavy Sword."""
    inventories = get_final_inventories(traj_json)

    # Count resources
    ironore = count_item_in_inventories(inventories, 'ironore')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    coal = count_item_in_inventories(inventories, 'coal')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')

    # Iron ore or smelted bars count (since bars are made from ore)
    iron_total = ironore + ironbar
    # Coal used for smelting counts toward coal mined
    # Each iron bar requires 1 coal, so if we have ironbar, we used coal
    coal_total = coal + ironbar  # coal remaining + coal used for bars

    has_iron = iron_total >= 8
    has_coal = coal_total >= 6
    has_ironbar = ironbar >= 6
    has_swords = heavysword >= 2

    alive = check_agents_alive(traj_json)

    passed = has_iron and has_coal and has_ironbar and has_swords and alive
    msg = f"Iron(ore+bar): {iron_total}/8, Coal(+used): {coal_total}/6, Iron Bar: {ironbar}/6, Heavy Sword: {heavysword}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 98."""
    return task_98_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_98_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
