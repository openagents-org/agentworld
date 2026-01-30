"""
Task 56 Success Criteria Verifier
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


def task_56_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Cross-Region Trading Network - craft 3x Silver Rings, 2x Axes, and 1x Heavy Sword."""
    inventories = get_final_inventories(traj_json)
    
    silverring = count_item_in_inventories(inventories, 'silverring')
    axe = count_item_in_inventories(inventories, 'axe')
    heavysword = count_item_in_inventories(inventories, 'sword2')

    has_rings = silverring >= 3
    has_axes = axe >= 2
    has_sword = heavysword >= 1

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_rings and has_axes and has_sword and alive
    msg = f"Silver Rings: {silverring}/3, Axes: {axe}/2, Heavy Sword: {heavysword}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 56."""
    return task_56_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_56_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
