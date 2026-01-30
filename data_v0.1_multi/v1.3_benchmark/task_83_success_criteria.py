"""
Task 83 Success Criteria Verifier
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


def task_83_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Ritual - 1x berylpendant, 1x goldring, 6x blueberry."""
    inventories = get_final_inventories(traj_json)

    berylpendant = count_item_in_inventories(inventories, 'berylpendant')
    goldring = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    blueberry = count_item_in_inventories(inventories, 'blueberry')

    pendant_passed = berylpendant >= 1
    ring_passed = goldring >= 1
    berry_passed = blueberry >= 6

    passed = pendant_passed and ring_passed and berry_passed
    msg = f"Beryl Pendant: {berylpendant}/1, Gold Ring: {goldring}/1, Blueberry: {blueberry}/6"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 83."""
    return task_83_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_83_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
