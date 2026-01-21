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
    """Cooking Guild.
    YAML criteria:
    - Team inventory contains 2x cornstew
    - Team inventory contains 2x cookedshrimp
    - Team inventory contains 2x cookedchicken
    - Team inventory contains 1x jellyfishsmoothie
    - All agents survive the cooking mission
    """
    inventories = get_final_inventories(traj_json)

    cornstew = count_item_in_inventories(inventories, 'cornstew')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    cookedchicken = count_item_in_inventories(inventories, 'cookedchicken')
    jellyfishsmoothie = count_item_in_inventories(inventories, 'jellyfishsmoothie')

    alive = check_agents_alive(traj_json)

    stew_ok = cornstew >= 2
    shrimp_ok = cookedshrimp >= 2
    chicken_ok = cookedchicken >= 2
    jelly_ok = jellyfishsmoothie >= 1

    success = stew_ok and shrimp_ok and chicken_ok and jelly_ok
    msg = f"Cornstew: {cornstew}/2, Cookedshrimp: {cookedshrimp}/2, Cookedchicken: {cookedchicken}/2, Jellyfishsmoothie: {jellyfishsmoothie}/1"
    return (1 if success else 0, msg)


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
