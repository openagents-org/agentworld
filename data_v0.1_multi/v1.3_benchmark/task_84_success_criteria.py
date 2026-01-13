"""
Task 84 Success Criteria Verifier
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


def task_84_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Tunnel Expedition - collect 8x ironore, 6x coal, defeat 3x Skeleton, craft 1x pickaxe."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and tools
    ironore = count_item_in_inventories(inventories, 'ironore')
    coal = count_item_in_inventories(inventories, 'coal')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')

    has_ironore = ironore >= 8
    has_coal = coal >= 6
    has_pickaxe = pickaxe >= 1

    # Check combat kills (3 skeletons)
    kills = count_combat_kills(traj_json, ['Skeleton', 'skeleton'])
    has_kills = kills >= 3

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_ironore and has_coal and has_pickaxe and has_kills and alive
    msg = f"Ironore: {ironore}/8, Coal: {coal}/6, Pickaxe: {pickaxe}/1, Kills: {kills}/3, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 84."""
    return task_84_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_84_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
