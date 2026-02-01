"""
Task 75 Relief Convoy V2 Success Criteria Verifier
Generated from: task_75_relief_convoy_v2.yaml
Description: Relief Convoy - Extended Supply Run (Harder)
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
    Relief Convoy - Extended Supply Run (Harder)

    Primary objective: Cook 12x Cooked Shrimp, craft 4x Pickaxe, and collect 16x logs
    """
    inventories = get_final_inventories(traj_json)
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    logs_count = count_item_in_inventories(inventories, 'logs')
    alive = check_agents_alive(traj_json)

    passed = cookedshrimp_count >= 12 and pickaxe_count >= 4 and logs_count >= 16 and alive
    msg = f"cookedshrimp: {cookedshrimp_count}/12, pickaxe: {pickaxe_count}/4, logs: {logs_count}/16, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_75_relief_convoy_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
