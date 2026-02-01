"""
Task 11 Lightning Staff V2 Success Criteria Verifier
Generated from: task_11_lightning_staff_v2.yaml
Description: Cooperative Lightning Staff Enhancement - Advanced Magic Crafting (Harder)
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
    Cooperative Lightning Staff Enhancement - Advanced Magic Crafting (Harder)

    Primary objective: Create TWO lightning staffs through full staff crafting and elemental enhancement chain
    """
    inventories = get_final_inventories(traj_json)
    lightningstaff_count = count_item_in_inventories(inventories, 'lightningstaff')

    passed = lightningstaff_count >= 2
    msg = f"Lightning staffs: {lightningstaff_count}/2"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_11_lightning_staff_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
