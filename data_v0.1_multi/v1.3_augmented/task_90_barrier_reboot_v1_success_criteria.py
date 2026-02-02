"""
Task 90 Barrier Reboot V1 Success Criteria Verifier
Generated from: task_90_barrier_reboot_v1.yaml
Description: Barrier Reboot - Quick Activation (Easier)
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
    Barrier Reboot - Quick Activation (Easier)

    Primary objective: Defeat Ancient Wizard at (163, 339), craft 1x Lightning Staff, and collect 5x goldnugget
    """
    inventories = get_final_inventories(traj_json)
    goldnugget_count = count_item_in_inventories(inventories, 'goldnugget')
    lightningstaff_count = count_item_in_inventories(inventories, 'lightningstaff')
    alive = check_agents_alive(traj_json)

    passed = goldnugget_count >= 5 and lightningstaff_count >= 1 and alive
    msg = f"goldnugget: {goldnugget_count}/5, lightningstaff: {lightningstaff_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_90_barrier_reboot_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
