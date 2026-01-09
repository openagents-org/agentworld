"""
Task 42 Success Criteria Verifier
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


def task_42_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Educational Training - all agents survive within 40 rounds."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 40

    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/40"
    return (1 if passed else 0, msg)


def task_42_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 49
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/49"
    return (1 if passed else 0, msg)


def task_42_verifier_v2(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 65
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/65"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 42."""
    return task_42_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_42_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
