"""
Task 31 Success Criteria Verifier
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


def task_31_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Woodworking Coordination."""
    inventories = get_final_inventories(traj_json)
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')
    arrows = count_item_in_inventories(inventories, 'arrow')
    msg = f"Wooden Bow: {woodenbow}, Arrows: {arrows}"
    return (1 if woodenbow >= 1 and arrows >= 10 else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 31."""
    return task_31_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_31_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
