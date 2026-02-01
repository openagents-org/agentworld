"""
Task 94 Maritime Trading V2 Success Criteria Verifier
Generated from: task_94_maritime_trading_v2.yaml
Description: Maritime Trading - Empire Trade (Harder)
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
    Maritime Trading - Empire Trade (Harder)

    Primary objective: Catch 16x rawshrimp, cook 12x Cooked Shrimp, and craft 4x Gold Ring
    """
    inventories = get_final_inventories(traj_json)
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    goldring_count = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    alive = check_agents_alive(traj_json)

    passed = rawshrimp_count >= 16 and cookedshrimp_count >= 12 and goldring_count >= 4 and alive
    msg = f"rawshrimp: {rawshrimp_count}/16, cookedshrimp: {cookedshrimp_count}/12, goldring: {goldring_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_94_maritime_trading_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
