"""
Task 95 Success Criteria Verifier
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


def task_95_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ocean Expedition - catch 8x rawshrimp, defeat Mermaid, cook 4x Cooked Shrimp."""
    inventories = get_final_inventories(traj_json)

    # Count resources
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')

    # Raw shrimp or cooked counts toward total shrimp caught
    shrimp_total = rawshrimp + cookedshrimp

    # Check Mermaid kill
    mermaid_kills = count_combat_kills(traj_json, ['Mermaid'])

    has_shrimp = shrimp_total >= 8
    has_mermaid = mermaid_kills >= 1
    has_cooked = cookedshrimp >= 4

    alive = check_agents_alive(traj_json)

    passed = has_shrimp and has_mermaid and has_cooked and alive
    msg = f"Shrimp(raw+cooked): {shrimp_total}/8, Mermaid killed: {mermaid_kills}/1, Cooked Shrimp: {cookedshrimp}/4, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 95."""
    return task_95_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_95_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
