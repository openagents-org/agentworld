"""
Task 36 Elite Skeleton Hunt V1 Success Criteria Verifier
Generated from: task_36_elite_skeleton_hunt_v1.yaml
Description: Elite Skeleton Hunt - Undead Elimination (Easier)
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
    Elite Skeleton Hunt - Undead Elimination (Easier)

    Primary objective: Defeat 2x Skeletons and collect 3x logs with pre-gathered starting materials
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')

    # Combat targets: {'Skeleton': 2}
    kills = count_combat_kills(traj_json, ['Skeleton'])
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 3 and kills >= 2 and alive
    msg = f"logs: {logs_count}/3, kills: {kills}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_36_elite_skeleton_hunt_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
