"""
Task 89 Beacon Calibration V1 Success Criteria Verifier
Generated from: task_89_beacon_calibration_v1.yaml
Description: Beacon Calibration - Quick Setup (Easier)
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
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Beacon Calibration - Quick Setup (Easier)

    Primary objective: Craft 1x Beryl Pendant and collect 5x logs and 4x icelogs
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    icelogs_count = count_item_in_inventories(inventories, 'icelogs')
    berylpendant_count = count_item_in_inventories(inventories, 'berylpendant')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 5 and icelogs_count >= 4 and berylpendant_count >= 1 and alive
    msg = f"logs: {logs_count}/5, icelogs: {icelogs_count}/4, berylpendant: {berylpendant_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_89_beacon_calibration_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
