"""
Task 73 Success Criteria Verifier
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


def task_73_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Biome Expedition.
    YAML criteria:
    - Team inventory contains at least 6x logs
    - 2x Goblin defeated
    - 1x Ogre defeated
    - Team inventory contains 1x woodenbow
    """
    inventories = get_final_inventories(traj_json)

    logs = count_item_in_inventories(inventories, 'logs')
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')

    goblin_kills = count_combat_kills(traj_json, ['Goblin', 'goblin'])
    ogre_kills = count_combat_kills(traj_json, ['Ogre', 'ogre'])

    logs_ok = logs >= 6
    goblin_ok = goblin_kills >= 2
    ogre_ok = ogre_kills >= 1
    bow_ok = woodenbow >= 1

    success = logs_ok and goblin_ok and ogre_ok and bow_ok
    msg = f"Logs: {logs}/6, Goblin kills: {goblin_kills}/2, Ogre kills: {ogre_kills}/1, Woodenbow: {woodenbow}/1"
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 73."""
    return task_73_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_73_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
