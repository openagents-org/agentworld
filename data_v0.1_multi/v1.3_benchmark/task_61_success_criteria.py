"""
Task 61 Success Criteria Verifier
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


def task_61_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Royal Banquet Preparation.
    YAML criteria:
    - Team inventory contains 3x cookedshrimp
    - Team inventory contains 2x tunasushi
    - Team inventory contains 2x cookedchicken
    - All agents survive the banquet preparation
    """
    inventories = get_final_inventories(traj_json)

    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    tunasushi = count_item_in_inventories(inventories, 'tunasushi')
    cookedchicken = count_item_in_inventories(inventories, 'cookedchicken')

    alive = check_agents_alive(traj_json)

    shrimp_ok = cookedshrimp >= 3
    sushi_ok = tunasushi >= 2
    chicken_ok = cookedchicken >= 2

    success = shrimp_ok and sushi_ok and chicken_ok and alive
    msg = f"Cookedshrimp: {cookedshrimp}/3, Tunasushi: {tunasushi}/2, Cookedchicken: {cookedchicken}/2, All alive: {alive}"
    return (1 if success else 0, msg)


def task_61_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    counts = aggregate_item_counts(inventories)
    cooked_food_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                        "cookedmeat", "jellyfishsmoothie", "stew", "stew2"]
    specialty_keys = ["silverring", "goldring", "goldenring", "berylpendant", "emeraldpendant",
                      "topazring", "magicstaff", "lightningstaff", "firestaff", "icestaff"]
    rare_ingredient_keys = ["rawshrimp", "rawtuna", "jellyfish", "crab", "fish", "herb",
                            "blueberry", "corn", "tomato", "apple", "logs", "ironore", "coal"]
    cooked_food = sum(counts.get(k, 0) for k in cooked_food_keys)
    specialty = sum(counts.get(k, 0) for k in specialty_keys)
    rare_ingredients = sum(counts.get(k, 0) for k in rare_ingredient_keys)
    success = cooked_food >= 8 and specialty >= 4 and rare_ingredients >= 60
    msg = (f"Cooked dishes: {cooked_food}/8, Specialty items: {specialty}/4, "
           f"Rare ingredients: {rare_ingredients}/60")
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 61."""
    return task_61_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_61_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
