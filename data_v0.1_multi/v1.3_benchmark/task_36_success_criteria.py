"""
Task 36 Success Criteria Verifier
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
    verify_combat,
    count_attack_actions,
    count_crafted_items,
    check_crafted_items,
    count_chat_messages,
    get_agent_items_by_username,
)


def task_36_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Skeleton Hunt - defeat 3x Skeletons and collect 3x logs."""
    kills = verify_combat(traj_json, 'skeleton')
    # print(get_final_inventories(traj_json))
    logs = count_item_in_inventories(get_final_inventories(traj_json), 'logs')
    all_alive = sum(1 if v > 0 else 0 for k, v in get_final_hp(traj_json).items())
    return (1 if kills >= 3 and logs >= 3 else 0, f"Kills: {kills}/3 (Skeletons), Logs: {logs}/3, Alive Agents: {all_alive}/3")


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 36."""
    return task_36_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_36_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
