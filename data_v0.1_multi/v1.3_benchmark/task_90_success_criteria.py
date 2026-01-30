"""
Task 90 Success Criteria Verifier
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


def task_90_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Barrier Reboot - defeat Ancient Wizard, collect 8x goldore, craft 1x lightningstaff, 1x firestaff."""
    inventories = get_final_inventories(traj_json)

    # Check for resources and staffs
    goldore = count_item_in_inventories(inventories, 'goldore')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')

    has_goldore = goldore >= 8
    has_lightning = lightningstaff >= 1
    has_fire = firestaff >= 1

    # Check combat kills (Ancient Wizard)
    kills = count_combat_kills(traj_json, ['Ancient Wizard', 'Wizard'])
    has_kills = kills >= 1

    passed = has_goldore and has_lightning and has_fire and has_kills
    msg = f"Goldore: {goldore}/8, Lightning: {lightningstaff}/1, Fire: {firestaff}/1, Kills: {kills}/1"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 90."""
    return task_90_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_90_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
