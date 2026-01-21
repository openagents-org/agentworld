"""
Task 35 Success Criteria Verifier
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
    verify_combat,
)


def task_35_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Combat Training - defeat 4x Goblins."""
    # Check combat kills (4 goblins)
    kills = verify_combat(traj_json, 'goblin')
    hps = get_final_agent_hp_simple(traj_json)
    print(hps)
    all_alive = sum(v > 0 for k, v in hps.items())
    return (1 if kills >= 4 else 0, f"Kills: {kills}/4 (Goblins), alive agents: {all_alive}/3")


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 35."""
    return task_35_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_35_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
