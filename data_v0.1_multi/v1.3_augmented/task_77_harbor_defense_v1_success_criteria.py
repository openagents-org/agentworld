"""
Task 77 Harbor Defense V1 Success Criteria Verifier
Generated from: task_77_harbor_defense_v1.yaml
Description: Harbor Defense - Single Boss (Easier)
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
    Harbor Defense - Single Boss (Easier)

    Primary objective: Defeat the Water Guardian at (197, 633) and craft 1x Wooden Bow
    """
    inventories = get_final_inventories(traj_json)
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')

    # Combat targets: {'Water Guardian': 1}
    kills = count_combat_kills(traj_json, ['Water Guardian'])
    alive = check_agents_alive(traj_json)

    passed = woodenbow_count >= 1 and kills >= 1 and alive
    msg = f"woodenbow: {woodenbow_count}/1, kills: {kills}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_77_harbor_defense_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
