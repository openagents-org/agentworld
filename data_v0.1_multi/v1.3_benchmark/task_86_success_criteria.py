"""
Task 86 Success Criteria Verifier
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


def task_86_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Tri-Forge Vanguard."""
    inventories = get_final_inventories(traj_json)
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')
    
    success = heavysword >= 4 and goldenbow >= 3 and lightningstaff >= 2 and firestaff >= 2
    msg = f"Heavy swords: {heavysword}/4, Golden bows: {goldenbow}/3, Lightning staffs: {lightningstaff}/2, Fire staffs: {firestaff}/2"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 86."""
    return task_86_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_86_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
