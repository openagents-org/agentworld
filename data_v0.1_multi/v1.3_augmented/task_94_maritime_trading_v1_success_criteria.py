"""
Task 94 Maritime Trading V1 Success Criteria Verifier
Generated from: task_94_maritime_trading_v1.yaml
Description: Maritime Trading - Quick Trade (Easier)
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
    Maritime Trading - Quick Trade (Easier)

    Primary objective: Catch 4x rawshrimp, cook 3x Cooked Shrimp, and craft 1x Gold Ring
    """
    inventories = get_final_inventories(traj_json)
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    goldring_count = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    alive = check_agents_alive(traj_json)

    passed = rawshrimp_count >= 4 and cookedshrimp_count >= 3 and goldring_count >= 1 and alive
    msg = f"rawshrimp: {rawshrimp_count}/4, cookedshrimp: {cookedshrimp_count}/3, goldring: {goldring_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_94_maritime_trading_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
