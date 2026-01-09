"""
Task 19 Success Criteria Verifier
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


def task_19_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Farm Defense - corn_harvester needs 8+ corn, tomato_gatherer needs 4+ tomato."""
    agent_items = get_agent_items_by_username(traj_json)

    corn_harvester_items = {}
    for username, items in agent_items.items():
        if "corn_harvester" in username.lower():
            corn_harvester_items = items
            break

    tomato_gatherer_items = {}
    for username, items in agent_items.items():
        if "tomato_gatherer" in username.lower():
            tomato_gatherer_items = items
            break

    corn = corn_harvester_items.get("corn", 0)
    tomato = tomato_gatherer_items.get("tomato", 0)

    corn_passed = corn >= 8
    tomato_passed = tomato >= 4
    passed = corn_passed and tomato_passed

    msg = f"corn: {corn}/8, tomato: {tomato}/4"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 19."""
    return task_19_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_19_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
