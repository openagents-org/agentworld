"""
Task 62 Weaponsmith Consortium V2 Success Criteria Verifier
Generated from: task_62_weaponsmith_consortium_v2.yaml
Description: Weaponsmith Consortium - Full Arsenal (Harder)
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
    Weaponsmith Consortium - Full Arsenal (Harder)

    Primary objective: Forge complete arsenal: 2 golden swords, 1 golden bow, 4 heavy swords, 4 axes, 1 pickaxe
    """
    inventories = get_final_inventories(traj_json)
    goldensword_count = count_item_in_inventories(inventories, 'goldensword')
    goldenbow_count = count_item_in_inventories(inventories, 'goldenbow')
    sword2_count = count_item_in_inventories(inventories, 'sword2')
    axe_count = count_item_in_inventories(inventories, 'axe')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    alive = check_agents_alive(traj_json)

    passed = goldensword_count >= 2 and goldenbow_count >= 1 and sword2_count >= 4 and axe_count >= 4 and pickaxe_count >= 1 and alive
    msg = f"goldensword: {goldensword_count}/2, goldenbow: {goldenbow_count}/1, sword2: {sword2_count}/4, axe: {axe_count}/4, pickaxe: {pickaxe_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_62_weaponsmith_consortium_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
