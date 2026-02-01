"""
Task 01 Magic Staff V1 Success Criteria Verifier
Generated from: task_01_magic_staff_v1.yaml
Description: Cooperative Magic Staff Crafting - Wizard Equipment Preparation (Easier)
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
    Cooperative Magic Staff Crafting - Wizard Equipment Preparation (Easier)

    Primary objective: Prepare wizard_agent with crafted magic staff for magical combat
    """
    inventories = get_final_inventories(traj_json)
    has_staff = has_item_in_any_inventory(inventories, 'staff')

    passed = has_staff
    msg = f"Staff crafted: {has_staff}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_01_magic_staff_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
