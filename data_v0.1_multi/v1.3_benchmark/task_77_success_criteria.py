"""
Task 77 Success Criteria Verifier
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


def task_77_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harbor Defense - defeat Water Guardian and Mermaid, craft 2 wooden bows."""
    # Check combat kills (2 bosses)
    kills = count_combat_kills(traj_json, ['Water Guardian', 'Mermaid', 'Guardian'])

    # Check for wooden bows
    inventories = get_final_inventories(traj_json)
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')

    kills_passed = kills >= 2
    bow_passed = woodenbow >= 2

    passed = kills_passed and bow_passed
    msg = f"Boss kills: {kills}/2, Wooden Bow: {woodenbow}/2"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 77."""
    return task_77_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_77_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
