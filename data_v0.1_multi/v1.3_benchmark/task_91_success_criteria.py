"""
Task 91 Success Criteria Verifier
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


def task_91_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Royal Tournament - defeat Iron Ogre, Hermit Crab Warrior, and Ogre Guardian."""
    # Check combat kills for all three bosses
    iron_ogre_kills = count_combat_kills(traj_json, ['Iron Ogre', 'IronOgre'])
    hermit_crab_kills = count_combat_kills(traj_json, ['Hermit Crab Warrior', 'HermitCrabWarrior', 'Hermit Crab'])
    ogre_guardian_kills = count_combat_kills(traj_json, ['Ogre Guardian', 'OgreGuardian'])

    has_iron_ogre = iron_ogre_kills >= 1
    has_hermit_crab = hermit_crab_kills >= 1
    has_ogre_guardian = ogre_guardian_kills >= 1

    alive = check_agents_alive(traj_json)

    passed = has_iron_ogre and has_hermit_crab and has_ogre_guardian and alive
    msg = f"Iron Ogre: {iron_ogre_kills}/1, Hermit Crab: {hermit_crab_kills}/1, Ogre Guardian: {ogre_guardian_kills}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


# =============================================================================
# CONSTRUCTION TASKS (41, 43, 74, 76, 81, 84, 87, 89, 90, 93)
# =============================================================================


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 91."""
    return task_91_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_91_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
