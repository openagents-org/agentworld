"""
Task 81 Elemental Grid V2 Success Criteria Verifier
Generated from: task_81_elemental_grid_v2.yaml
Description: Elemental Grid - Full Array (Harder)
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
    Elemental Grid - Full Array (Harder)

    Primary objective: Collect 12x icelogs and 10x logs, and craft 4x Magic Staff
    """
    inventories = get_final_inventories(traj_json)
    icelogs_count = count_item_in_inventories(inventories, 'icelogs')
    logs_count = count_item_in_inventories(inventories, 'logs')
    staff_count = count_item_in_inventories(inventories, 'staff')
    alive = check_agents_alive(traj_json)

    passed = icelogs_count >= 12 and logs_count >= 10 and staff_count >= 4 and alive
    msg = f"icelogs: {icelogs_count}/12, logs: {logs_count}/10, staff: {staff_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_81_elemental_grid_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
