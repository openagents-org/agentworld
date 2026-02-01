"""
Task 59 Elite Merchant Guild V1 Success Criteria Verifier
Generated from: task_59_elite_merchant_guild_v1.yaml
Description: Elite Merchant Guild (Easier)
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
    Elite Merchant Guild (Easier)

    Primary objective: Craft 1x Gold Ring, 1x Staff, and 1x Pickaxe using provided materials
    """
    inventories = get_final_inventories(traj_json)
    goldring_count = count_item_in_inventories(inventories, 'goldring')
    staff_count = count_item_in_inventories(inventories, 'staff')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    alive = check_agents_alive(traj_json)

    passed = goldring_count >= 1 and staff_count >= 1 and pickaxe_count >= 1 and alive
    msg = f"goldring: {goldring_count}/1, staff: {staff_count}/1, pickaxe: {pickaxe_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_59_elite_merchant_guild_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
