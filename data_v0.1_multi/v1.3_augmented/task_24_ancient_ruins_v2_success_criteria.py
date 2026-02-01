"""
Task 24 Ancient Ruins V2 Success Criteria Verifier
Generated from: task_24_ancient_ruins_v2.yaml
Description: Ancient Ruins Exploration - Archaeological Treasure Discovery (Harder)
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
    Ancient Ruins Exploration - Archaeological Treasure Discovery (Harder)

    Primary objective: Successfully defeat BOTH Golden Golem AND Giant Spider, plus explore all treasure chambers
    """
    # Check combat kills (v2 = harder, need 2 guardians)
    kills = count_combat_kills(traj_json, ['Golden Golem', 'Golem', 'Big Baby Spooder', 'Spooder', 'Giant Spider'])
    alive = check_agents_alive(traj_json)

    passed = kills >= 2 and alive
    msg = f"Guardian kills: {kills}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_24_ancient_ruins_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
