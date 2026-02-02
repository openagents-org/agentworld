"""
Task 47 Magic Staff Forge V1 Success Criteria Verifier
Generated from: task_47_magic_staff_forge_v1.yaml
Description: Magic Staff Forge - Elemental Staff Production (Easier)
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
    Magic Staff Forge - Elemental Staff Production (Easier)

    Primary objective: Craft 1x Lightning Staff using pre-crafted staff and materials
    """
    inventories = get_final_inventories(traj_json)
    lightningstaff_count = count_item_in_inventories(inventories, 'lightningstaff')
    alive = check_agents_alive(traj_json)

    passed = lightningstaff_count >= 1 and alive
    msg = f"lightningstaff: {lightningstaff_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_47_magic_staff_forge_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
