"""
Task 100 Success Criteria Verifier
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


def task_100_verifier(traj_json: Dict) -> Tuple[int, str]:
    """World Resource Survey."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    
    resource_types = ['logs', 'ironore', 'coal', 'goldore', 'blueberry', 'corn', 'rawshrimp']
    found_types = sum(1 for r in resource_types if count_item_in_inventories(inventories, r) > 0)
    
    success = alive and found_types >= 5
    msg = f"All alive: {alive}, Resource types found: {found_types}/5"
    return (1 if success else 0, msg)


# =============================================================================
# SPECIALIZED TASKS FROM verify/ FOLDER
# =============================================================================


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 100."""
    return task_100_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_100_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
