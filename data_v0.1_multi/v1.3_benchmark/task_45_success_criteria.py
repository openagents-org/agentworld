"""
Task 45 Success Criteria Verifier
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


def task_45_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Caravan Escort - miner_agent must have 3+ goldore, 2+ kills, all survive."""
    # Check miner_agent inventory for goldore
    agent_items = get_agent_items_by_username(traj_json)
    miner_items = agent_items.get('miner_agent', {})
    goldore = miner_items.get('goldore', 0)
    has_goldore = goldore >= 3

    # Check combat kills (by guards)
    kills = count_combat_kills(traj_json, ['hostile', 'creature', 'enemy', 'monster'])
    has_kills = kills >= 2

    # Check all agents alive
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    passed = has_goldore and has_kills and all_alive
    msg = f"Miner goldore: {goldore}/3, Kills: {kills}/2, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def task_45_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 57
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/57"
    return (1 if passed else 0, msg)


def task_45_verifier_v2(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 77
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/77"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 45."""
    return task_45_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_45_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
