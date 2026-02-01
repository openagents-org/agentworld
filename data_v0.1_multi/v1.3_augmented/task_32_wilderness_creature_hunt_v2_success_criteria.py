"""
Task 32 Wilderness Creature Hunt V2 Success Criteria Verifier
Generated from: task_32_wilderness_creature_hunt_v2.yaml
Description: Wilderness Creature Hunt - Wolf Pack Elimination (Harder)
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
    Wilderness Creature Hunt - Wolf Pack Elimination (Harder)

    Primary objective: Defeat 6x Wolves and collect 8x logs from the wilderness forest area
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')

    # Combat targets: {'Wolve': 6}
    kills = count_combat_kills(traj_json, ['Wolve'])
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 8 and kills >= 6 and alive
    msg = f"logs: {logs_count}/8, kills: {kills}/6, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_32_wilderness_creature_hunt_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
