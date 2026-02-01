"""
Task 96 Mountain Rescue V2 Success Criteria Verifier
Generated from: task_96_mountain_rescue_v2.yaml
Description: Mountain Rescue - Full Supply Chain (Harder)
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
    Mountain Rescue - Full Supply Chain (Harder)

    Primary objective: Collect 12x logs, 14x ironore, cook 8x Cooked Shrimp, and craft 4x Pickaxe
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 12 and ironore_count >= 14 and cookedshrimp_count >= 8 and pickaxe_count >= 4 and alive
    msg = f"logs: {logs_count}/12, ironore: {ironore_count}/14, cookedshrimp: {cookedshrimp_count}/8, pickaxe: {pickaxe_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_96_mountain_rescue_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
