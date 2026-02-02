"""
Task 79 Success Criteria Verifier
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


def task_79_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Dragon Hunt - defeat Iron Ogre, Water Guardian, and Mermaid."""
    # Check combat kills (3 bosses) - agent survival not required
    kills = count_combat_kills(traj_json, ['Iron Ogre', 'Water Guardian', 'Mermaid', 'Ogre', 'Guardian'])

    passed = kills >= 3
    msg = f"Boss kills: {kills}/3"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 79."""
    return task_79_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_79_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
