"""
Task 91 Royal Tournament V2 Success Criteria Verifier
Generated from: task_91_royal_tournament_v2.yaml
Description: Royal Tournament - Five Boss Gauntlet (Harder)
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
    Royal Tournament - Five Boss Gauntlet (Harder)

    Primary objective: Defeat Dark Ogre at (238, 48), Hermit Crab at (224, 359), Ogre at (291, 644), Jellyfish at (197, 633), and Wolf at (1016, 682)
    """
    # Check combat kills (v2 = harder, need 5 bosses)
    kills = count_combat_kills(traj_json, ['Dark Ogre', 'Iron Ogre', 'Ogre', 'Hermit Crab',
                                           'Ogre Guardian', 'Jellyfish', 'Wolf', 'Dark Wolf'])
    alive = check_agents_alive(traj_json)

    passed = kills >= 5 and alive
    msg = f"Boss kills: {kills}/5, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_91_royal_tournament_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
