"""
Task 85 Ice Convoy V1 Success Criteria Verifier
Generated from: task_85_ice_convoy_v1.yaml
Description: Ice Convoy - Quick Expedition (Easier)
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
    Ice Convoy - Quick Expedition (Easier)

    Primary objective: Collect 6x icelogs and 3x rawshrimp, and craft 1x Magic Staff
    """
    inventories = get_final_inventories(traj_json)
    icelogs_count = count_item_in_inventories(inventories, 'icelogs')
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    staff_count = count_item_in_inventories(inventories, 'staff')
    alive = check_agents_alive(traj_json)

    passed = icelogs_count >= 6 and rawshrimp_count >= 3 and staff_count >= 1 and alive
    msg = f"icelogs: {icelogs_count}/6, rawshrimp: {rawshrimp_count}/3, staff: {staff_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_85_ice_convoy_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
