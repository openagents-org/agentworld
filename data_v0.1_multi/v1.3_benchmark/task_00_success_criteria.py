"""
Task 00 Success Criteria Verifier
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


def task_00_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Cooperative Workshop - 3 projects: staff, 10 arrows, silver ring."""
    inventories = get_final_inventories(traj_json)
    
    staff = has_item_in_any_inventory(inventories, 'staff')
    arrows = count_item_in_inventories(inventories, 'arrow')
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    
    success = staff and arrows >= 10 and silverring
    msg = f"Staff: {staff}, Arrows: {arrows}/10, Silver ring: {silverring}"
    return (1 if success else 0, msg)


def task_00_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    arrows = count_item_in_inventories(inventories, 'arrow')
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    success = staff and arrows >= 15 and silverring
    msg = f"Staff: {staff}, Arrows: {arrows}/15, Silver ring: {silverring}"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 00."""
    return task_00_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_00_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
