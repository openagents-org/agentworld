"""
Task 65 Success Criteria Verifier
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


def task_65_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Alchemist Guild Potions."""
    inventories = get_final_inventories(traj_json)
    potions = ['healthpotion', 'manapotion', 'jellyfishsmoothie']
    potion_count = sum(count_item_in_inventories(inventories, p) for p in potions)
    msg = f"Potions/consumables: {potion_count}"
    return (1 if potion_count >= 5 else 0, msg)


def task_65_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    consumables = ["healthpotion", "manapotion", "jellyfishsmoothie",
                   "cookedshrimp", "cookedchicken", "cookedbeef", "stew", "stew2",
                   "cookedtuna", "cookedmeat"]
    total = sum(count_item_in_inventories(inventories, c) for c in consumables)
    msg = f"Consumables: {total}/10"
    return (1 if total >= 10 else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 65."""
    return task_65_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_65_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
