"""
Task 43 Success Criteria Verifier
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


def task_43_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forest Cleanup - defeat 5x Rats and collect 4x blueberry."""
    inventories = get_final_inventories(traj_json)

    # Check for blueberry
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    has_blueberry = blueberry >= 4

    # Check combat kills (5 rats)
    kills = count_combat_kills(traj_json, ['Rat', 'rat'])
    has_kills = kills >= 5

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_blueberry and has_kills and alive
    msg = f"Blueberry: {blueberry}/4, Kills: {kills}/5, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 43."""
    return task_43_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_43_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
