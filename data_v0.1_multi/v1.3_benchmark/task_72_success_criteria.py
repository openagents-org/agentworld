"""
Task 72 Success Criteria Verifier
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


def task_72_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress Defense - craft 2x Heavy Sword, defeat 6x Goblin and 4x Skeleton."""
    inventories = get_final_inventories(traj_json)

    # Check for heavy swords (sword2)
    sword2 = count_item_in_inventories(inventories, 'sword2') + count_item_in_inventories(inventories, 'heavysword')
    sword_ok = sword2 >= 2

    # Check combat kills (10 total: 6 goblins + 4 skeletons)
    goblin_kills = count_combat_kills(traj_json, ['Goblin', 'goblin'])
    skeleton_kills = count_combat_kills(traj_json, ['Skeleton', 'skeleton'])
    goblin_ok = goblin_kills >= 6
    skeleton_ok = skeleton_kills >= 4

    passed = sword_ok and goblin_ok and skeleton_ok
    msg = f"Sword2: {sword2}/2, Goblin kills: {goblin_kills}/6, Skeleton kills: {skeleton_kills}/4"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 72."""
    return task_72_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_72_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
