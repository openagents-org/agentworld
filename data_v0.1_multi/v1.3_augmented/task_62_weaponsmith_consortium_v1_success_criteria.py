"""
Task 62 Weaponsmith Consortium V1 Success Criteria Verifier
Generated from: task_62_weaponsmith_consortium_v1.yaml
Description: Weaponsmith Consortium - Arsenal (Easier)
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
    Weaponsmith Consortium - Arsenal (Easier)

    Primary objective: Craft 1x Heavy Sword, 1x Axe, and 1x Pickaxe using provided bars
    """
    inventories = get_final_inventories(traj_json)
    sword2_count = count_item_in_inventories(inventories, 'sword2')
    axe_count = count_item_in_inventories(inventories, 'axe')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    alive = check_agents_alive(traj_json)

    passed = sword2_count >= 1 and axe_count >= 1 and pickaxe_count >= 1 and alive
    msg = f"sword2: {sword2_count}/1, axe: {axe_count}/1, pickaxe: {pickaxe_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_62_weaponsmith_consortium_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
