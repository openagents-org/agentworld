"""
Task 65 Cooking Guild V2 Success Criteria Verifier
Generated from: task_65_cooking_guild_v2.yaml
Description: Crafting Guild - Full Production (Harder)
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
    Crafting Guild - Full Production (Harder)

    Primary objective: Craft 2x Magic Staff, 2x Silver Ring, and gather 6x logs and 4x rawshrimp
    """
    inventories = get_final_inventories(traj_json)
    staff_count = count_item_in_inventories(inventories, 'staff')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    logs_count = count_item_in_inventories(inventories, 'logs')
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    has_magic = has_item_in_any_inventory(inventories, 'magic')
    has_silver = has_item_in_any_inventory(inventories, 'silver')
    alive = check_agents_alive(traj_json)

    passed = staff_count >= 2 and silverring_count >= 2 and logs_count >= 6 and rawshrimp_count >= 4 and has_magic and has_silver and alive
    msg = f"staff: {staff_count}/2, silverring: {silverring_count}/2, logs: {logs_count}/6, rawshrimp: {rawshrimp_count}/4, magic: {has_magic}, silver: {has_silver}, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_65_cooking_guild_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
