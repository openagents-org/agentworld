"""
Task 66 Success Criteria Verifier
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


def task_66_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Archery Competition.
    YAML criteria:
    - Team inventory contains 1x goldenbow
    - Team inventory contains at least 20x arrow
    - All agents survive the production mission
    """
    inventories = get_final_inventories(traj_json)

    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    arrows = count_item_in_inventories(inventories, 'arrow')

    alive = check_agents_alive(traj_json)

    bow_ok = goldenbow >= 1
    arrow_ok = arrows >= 20

    success = bow_ok and arrow_ok and alive
    msg = f"Goldenbow: {goldenbow}/1, Arrows: {arrows}/20, All alive: {alive}"
    return (1 if success else 0, msg)


def task_66_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    bows = (count_item_in_inventories(inventories, 'woodenbow') +
            count_item_in_inventories(inventories, 'bow') +
            count_item_in_inventories(inventories, 'goldenbow'))
    success = arrows >= 50 and bows >= 5
    msg = f"Arrows: {arrows}/50, Bows: {bows}/5"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 66."""
    return task_66_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_66_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
