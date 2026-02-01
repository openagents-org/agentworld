"""
Task 42 Skill Training V1 Success Criteria Verifier
Generated from: task_42_skill_training_v1.yaml
Description: Skill Training - Multi-Craft Production (Easier)
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
    Skill Training - Multi-Craft Production (Easier)

    Primary objective: Craft 1x staff using pre-gathered sticks
    """
    inventories = get_final_inventories(traj_json)
    staff_count = count_item_in_inventories(inventories, 'staff')
    alive = check_agents_alive(traj_json)

    passed = staff_count >= 1 and alive
    msg = f"staff: {staff_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_42_skill_training_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
