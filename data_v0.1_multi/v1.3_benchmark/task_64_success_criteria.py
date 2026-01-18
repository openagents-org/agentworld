"""
Task 64 Success Criteria Verifier
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


def task_64_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ice Region Survival Expedition.
    YAML criteria:
    - Team inventory contains at least 8x icelogs
    - 4x Ice Rat defeated
    - Team inventory contains 2x axe
    - All agents survive the expedition
    """
    inventories = get_final_inventories(traj_json)

    # Count icelogs (check various possible key names)
    icelogs = count_item_in_inventories(inventories, 'icelogs')
    if icelogs == 0:
        icelogs = count_item_in_inventories(inventories, 'icelog')

    axe = count_item_in_inventories(inventories, 'axe')

    # Count Ice Rat kills
    ice_rat_kills = count_combat_kills(traj_json, ['Ice Rat', 'IceRat', 'icerat', 'ice rat'])

    alive = check_agents_alive(traj_json)

    logs_ok = icelogs >= 8
    kills_ok = ice_rat_kills >= 4
    axe_ok = axe >= 2

    success = logs_ok and kills_ok and axe_ok and alive
    msg = f"Icelogs: {icelogs}/8, Ice Rat kills: {ice_rat_kills}/4, Axe: {axe}/2, All alive: {alive}"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 64."""
    return task_64_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_64_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
