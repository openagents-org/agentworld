"""
Task 27 Volcanic Forge V1 Success Criteria Verifier
Generated from: task_27_volcanic_forge_v1.yaml
Description: Southern Desert Expedition - Mining and Combat (Easier)
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
    Southern Desert Expedition - Mining and Combat (Easier)

    Primary objective: Successfully defeat Water Guardian and collect equipment drops with pre-gathered ore supplies
    """
    inventories = get_final_inventories(traj_json)

    # Check for valuable ores
    valuable_ores = ['goldnugget', 'nisocore', 'moonrockore', 'lapislazuli', 'beryl', 'topaz']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in valuable_ores)

    # Check combat kills
    kills = count_combat_kills(traj_json, ['Water Guardian', 'Ogre Guardian', 'Guardian'])

    alive = check_agents_alive(traj_json)

    passed = ore_count >= 1 and kills >= 1 and alive
    msg = f"Valuable ore: {ore_count}/1, Kills: {kills}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_27_volcanic_forge_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
