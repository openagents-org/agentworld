"""
Task 28 Success Criteria Verifier
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


def task_28_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Dark Forest Cleansing - defeat Dark Wolf boss and collect wolfarmor."""
    inventories = get_final_inventories(traj_json)

    # Check for wolfarmor drop from Dark Wolf - definitive proof of kill
    wolfarmor = has_item_in_any_inventory(inventories, 'wolfarmor')

    # Check combat kills (Dark Wolf) via observation/chat messages
    kills = count_combat_kills(traj_json, ['Dark Wolf', 'Wolf'])
    has_kills = kills >= 1

    # wolfarmor in inventory is definitive proof Dark Wolf was killed
    # (it only drops from Dark Wolf)
    boss_killed = wolfarmor or has_kills

    # Note: Primary objective is "defeat Dark Wolf and collect drops"
    # Survival is secondary criteria, not required for primary success
    alive = check_agents_alive(traj_json)

    # Primary objective: boss killed AND wolfarmor collected
    passed = boss_killed and wolfarmor
    msg = f"Wolfarmor: {wolfarmor}, Kills: {kills}/1 (boss_killed={boss_killed}), All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 28."""
    return task_28_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_28_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
