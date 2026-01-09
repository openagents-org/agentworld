"""
Task 50 Success Criteria Verifier
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


def task_50_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Combat Battalion - defeat 4 tiers of enemies."""
    alive = check_agents_alive(traj_json)
    hp_map = get_final_hp(traj_json)
    survivors = sum(1 for hp in hp_map.values() if hp > 0)
    total = len(hp_map)
    
    success = survivors >= 4  # At least 4 out of 5 survive
    msg = f"Survivors: {survivors}/{total}, All alive: {alive}"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 50."""
    return task_50_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_50_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
