"""
Task 90 Barrier Reboot V2 Success Criteria Verifier
Generated from: task_90_barrier_reboot_v2.yaml
Description: Barrier Reboot - Full System Reset (Harder)
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
    Barrier Reboot - Full System Reset (Harder)

    Primary objective: Defeat Ancient Wizard at (163, 339), Golden Golem at (548, 232), and Dark Ogre at (238, 48), craft 2x Lightning Staff and 2x Fire Staff, and collect 12x goldnugget
    """
    inventories = get_final_inventories(traj_json)
    goldnugget_count = count_item_in_inventories(inventories, 'goldnugget')
    lightningstaff_count = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff_count = count_item_in_inventories(inventories, 'firestaff')
    alive = check_agents_alive(traj_json)

    passed = goldnugget_count >= 12 and lightningstaff_count >= 2 and firestaff_count >= 2 and alive
    msg = f"goldnugget: {goldnugget_count}/12, lightningstaff: {lightningstaff_count}/2, firestaff: {firestaff_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_90_barrier_reboot_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
