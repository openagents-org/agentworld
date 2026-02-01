"""
Task 34 Enchanted Staff Workshop V2 Success Criteria Verifier
Generated from: task_34_enchanted_staff_workshop_v2.yaml
Description: Enchanted Staff Workshop - Lightning Staff Creation (Harder)
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
    Enchanted Staff Workshop - Lightning Staff Creation (Harder)

    Primary objective: Craft 2x Lightning Staffs by gathering materials and coordinating crafting operations
    """
    inventories = get_final_inventories(traj_json)
    lightningstaff_count = count_item_in_inventories(inventories, 'lightningstaff')
    alive = check_agents_alive(traj_json)

    passed = lightningstaff_count >= 2 and alive
    msg = f"lightningstaff: {lightningstaff_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_34_enchanted_staff_workshop_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
