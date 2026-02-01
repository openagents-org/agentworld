"""
Task 61 Royal Banquet V2 Success Criteria Verifier
Generated from: task_61_royal_banquet_v2.yaml
Description: Royal Banquet - Full Feast (Harder)
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
    Royal Banquet - Full Feast (Harder)

    Primary objective: Cook 6x Cooked Shrimp, 4x Cooked Tuna, and 4x Cooked Chicken
    """
    inventories = get_final_inventories(traj_json)
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    cookedtuna_count = count_item_in_inventories(inventories, 'cookedtuna')
    cookedchicken_count = count_item_in_inventories(inventories, 'cookedchicken')
    alive = check_agents_alive(traj_json)

    passed = cookedshrimp_count >= 6 and cookedtuna_count >= 4 and cookedchicken_count >= 4 and alive
    msg = f"cookedshrimp: {cookedshrimp_count}/6, cookedtuna: {cookedtuna_count}/4, cookedchicken: {cookedchicken_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_61_royal_banquet_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
