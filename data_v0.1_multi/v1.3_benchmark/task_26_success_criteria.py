"""
Task 26 Success Criteria Verifier
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


def task_26_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Desert Caravan Trading - mine ore, defeat creature, transfer items, chat 3+ times."""
    inventories = get_final_inventories(traj_json)

    # Check for mined ores (any ore type)
    ores = ['ironore', 'goldore', 'coal', 'copperore', 'tinore']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)
    has_ore = ore_count >= 1

    # Check combat kills (desert creature)
    kills = count_combat_kills(traj_json, ['cactus', 'scorpion', 'vulture', 'Cactus', 'Scorpion', 'Vulture'])
    has_kills = kills >= 1

    # Check chat messages (coordination)
    chat_count = count_chat_messages(traj_json)
    has_chat = chat_count >= 3

    # Check all agents alive
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    passed = has_ore and has_kills and has_chat and all_alive
    msg = f"Ore: {ore_count}/1, Kills: {kills}/1, Chat: {chat_count}/3, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 26."""
    return task_26_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_26_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
