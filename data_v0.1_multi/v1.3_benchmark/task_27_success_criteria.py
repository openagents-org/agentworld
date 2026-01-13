"""
Task 27 Success Criteria Verifier
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


def task_27_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Volcanic Forge - mine valuable ore, defeat Water Guardian and Ogre Guardian."""
    inventories = get_final_inventories(traj_json)

    # Check for valuable ores (gold, ibo, taaffeite, moonrock, lapis)
    valuable_ores = ['goldore', 'ibo', 'taaffeite', 'moonrock', 'lapislazuli']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in valuable_ores)
    has_ore = ore_count >= 1

    # Check combat kills (need to defeat 2 guardians)
    kills = count_combat_kills(traj_json, ['Water Guardian', 'Ogre Guardian', 'Guardian'])
    has_kills = kills >= 2

    # Check all agents alive
    alive = check_agents_alive(traj_json)

    passed = has_ore and has_kills and alive
    msg = f"Valuable ore: {ore_count}/1, Kills: {kills}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 27."""
    return task_27_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_27_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
