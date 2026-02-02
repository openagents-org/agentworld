"""
Task 89 Beacon Calibration V2 Success Criteria Verifier
Generated from: task_89_beacon_calibration_v2.yaml
Description: Beacon Calibration - Full Array (Harder)
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
    Beacon Calibration - Full Array (Harder)

    Primary objective: Craft 2x Beryl Pendant, 2x Lightning Staff, and collect 12x logs and 10x icelogs
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    icelogs_count = count_item_in_inventories(inventories, 'icelogs')
    berylpendant_count = count_item_in_inventories(inventories, 'berylpendant')
    lightningstaff_count = count_item_in_inventories(inventories, 'lightningstaff')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 12 and icelogs_count >= 10 and berylpendant_count >= 2 and lightningstaff_count >= 2 and alive
    msg = f"logs: {logs_count}/12, icelogs: {icelogs_count}/10, berylpendant: {berylpendant_count}/2, lightningstaff: {lightningstaff_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_89_beacon_calibration_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
