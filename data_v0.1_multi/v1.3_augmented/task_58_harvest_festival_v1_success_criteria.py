"""
Task 58 Harvest Festival V1 Success Criteria Verifier
Generated from: task_58_harvest_festival_v1.yaml
Description: Festival Crafting - Celebration Prep (Easier)
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
    Festival Crafting - Celebration Prep (Easier)

    Primary objective: Craft 1x Magic Staff and 1x Silver Ring through coordinated material transfers
    """
    inventories = get_final_inventories(traj_json)
    staff_count = count_item_in_inventories(inventories, 'staff')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    alive = check_agents_alive(traj_json)

    passed = staff_count >= 1 and silverring_count >= 1 and alive
    msg = f"staff: {staff_count}/1, silverring: {silverring_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_58_harvest_festival_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
