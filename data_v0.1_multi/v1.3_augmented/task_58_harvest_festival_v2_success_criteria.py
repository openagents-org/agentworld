"""
Task 58 Harvest Festival V2 Success Criteria Verifier
Generated from: task_58_harvest_festival_v2.yaml
Description: Festival Crafting - Large Scale Production (Harder)
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
    Festival Crafting - Large Scale Production (Harder)

    Primary objective: Craft 3x Magic Staff, 4x Silver Rings, and 2x Wooden Bows
    """
    inventories = get_final_inventories(traj_json)
    staff_count = count_item_in_inventories(inventories, 'staff')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')
    has_magic = has_item_in_any_inventory(inventories, 'magic')
    has_silver = has_item_in_any_inventory(inventories, 'silver')
    has_wooden = has_item_in_any_inventory(inventories, 'wooden')
    alive = check_agents_alive(traj_json)

    passed = staff_count >= 3 and silverring_count >= 4 and woodenbow_count >= 2 and has_magic and has_silver and has_wooden and alive
    msg = f"staff: {staff_count}/3, silverring: {silverring_count}/4, woodenbow: {woodenbow_count}/2, magic: {has_magic}, silver: {has_silver}, wooden: {has_wooden}, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_58_harvest_festival_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
