"""
Task 42 Skill Training V2 Success Criteria Verifier
Generated from: task_42_skill_training_v2.yaml
Description: Skill Training - Multi-Craft Production (Harder)
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
    Skill Training - Multi-Craft Production (Harder)

    Primary objective: Craft 2x staff and 2x silverring through coordinated skill practice
    """
    inventories = get_final_inventories(traj_json)
    staff_count = count_item_in_inventories(inventories, 'staff')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    alive = check_agents_alive(traj_json)

    passed = staff_count >= 2 and silverring_count >= 2 and alive
    msg = f"staff: {staff_count}/2, silverring: {silverring_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_42_skill_training_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
