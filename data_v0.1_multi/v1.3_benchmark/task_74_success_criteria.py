"""
Task 74 Success Criteria Verifier
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


def task_74_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Guild Equipment.
    YAML criteria:
    - Team inventory contains 2x sword2 (heavy sword)
    - Team inventory contains 1x axe
    - Team inventory contains 1x woodenbow
    - Team inventory contains 2x silverring
    """
    inventories = get_final_inventories(traj_json)

    sword2 = count_item_in_inventories(inventories, 'sword2') + count_item_in_inventories(inventories, 'heavysword')
    axe = count_item_in_inventories(inventories, 'axe')
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')
    silverring = count_item_in_inventories(inventories, 'silverring')

    sword_ok = sword2 >= 2
    axe_ok = axe >= 1
    bow_ok = woodenbow >= 1
    ring_ok = silverring >= 2

    success = sword_ok and axe_ok and bow_ok and ring_ok
    msg = f"Sword2/HeavySword: {sword2}/2, Axe: {axe}/1, Woodenbow: {woodenbow}/1, Silverring: {silverring}/2"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 74."""
    return task_74_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_74_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
