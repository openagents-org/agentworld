"""
Task 53 Success Criteria Verifier
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


def task_53_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Culinary Expedition - cook 4x Cooked Shrimp, 2x Tuna Sushi, and 1x Jellyfish Smoothie."""
    inventories = get_final_inventories(traj_json)
    
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    tunasushi = count_item_in_inventories(inventories, 'tunasushi')
    jellyfishsmoothie = count_item_in_inventories(inventories, 'jellyfishsmoothie')
    
    has_shrimp = cookedshrimp >= 4
    has_tuna = tunasushi >= 2
    has_jellyfish = jellyfishsmoothie >= 1
    
    # Check all agents alive
    alive = check_agents_alive(traj_json)
    
    passed = has_shrimp and has_tuna and has_jellyfish and alive
    msg = f"Cooked Shrimp: {cookedshrimp}/4, Tuna Sushi: {tunasushi}/2, Jellyfish Smoothie: {jellyfishsmoothie}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 53."""
    return task_53_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_53_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
