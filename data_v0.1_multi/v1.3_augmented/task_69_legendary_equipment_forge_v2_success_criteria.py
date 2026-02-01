"""
Task 69 Legendary Equipment Forge V2 Success Criteria Verifier
Generated from: task_69_legendary_equipment_forge_v2.yaml
Description: Legendary Equipment Forge - Extended Challenge (Harder)
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
    Legendary Equipment Forge - Extended Challenge (Harder)

    Primary objective: Forge 4x golden items, 3x magic staffs, and 5x elite weapons
    """
    inventories = get_final_inventories(traj_json)
    goldensword_count = count_item_in_inventories(inventories, 'goldensword')
    goldenboots_count = count_item_in_inventories(inventories, 'goldenboots')
    goldring_count = count_item_in_inventories(inventories, 'goldring')
    staff_count = count_item_in_inventories(inventories, 'staff')
    sword2_count = count_item_in_inventories(inventories, 'sword2')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    axe_count = count_item_in_inventories(inventories, 'axe')
    master_count = count_item_in_inventories(inventories, 'master')
    alive = check_agents_alive(traj_json)

    passed = goldensword_count >= 1 and goldenboots_count >= 1 and goldring_count >= 2 and staff_count >= 3 and sword2_count >= 2 and pickaxe_count >= 2 and axe_count >= 1 and master_count >= 9 and alive
    msg = f"goldensword: {goldensword_count}/1, goldenboots: {goldenboots_count}/1, goldring: {goldring_count}/2, staff: {staff_count}/3, sword2: {sword2_count}/2, pickaxe: {pickaxe_count}/2, axe: {axe_count}/1, master: {master_count}/9, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_69_legendary_equipment_forge_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
