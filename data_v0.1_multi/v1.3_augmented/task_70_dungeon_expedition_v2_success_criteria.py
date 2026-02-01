"""
Task 70 Dungeon Expedition V2 Success Criteria Verifier
Generated from: task_70_dungeon_expedition_v2.yaml
Description: Dungeon Expedition - Triple Boss Hunt (Harder)
"""

import sys
from pathlib import Path

# Add benchmark directory to path for verifier_utils
sys.path.insert(0, str(Path(__file__).parent.parent / "v1.3_benchmark"))

from typing import Dict, Tuple
from verifier_utils import (
    get_final_inventories,
    count_item_in_inventories,
    has_item_in_any_inventory,
    check_agents_alive,
    count_combat_kills,
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Dungeon Expedition - Triple Boss Hunt (Harder)

    Primary objective: Defeat Dark Ogre, Ogre, AND Ogre Chieftain, then craft 4x Heavy Sword
    """
    inventories = get_final_inventories(traj_json)
    sword2_count = count_item_in_inventories(inventories, 'sword2')

    # Combat targets: {'Dark Ogre': 1, 'Ogre': 1, 'Ogre Chieftain': 1}
    kills = count_combat_kills(traj_json, ['Dark Ogre', 'Ogre', 'Ogre Chieftain'])
    alive = check_agents_alive(traj_json)

    passed = sword2_count >= 4 and kills >= 3 and alive
    msg = f"sword2: {sword2_count}/4, kills: {kills}/3, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_70_dungeon_expedition_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
