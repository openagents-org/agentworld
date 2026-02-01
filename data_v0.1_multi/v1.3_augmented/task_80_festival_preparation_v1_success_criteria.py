"""
Task 80 Festival Preparation V1 Success Criteria Verifier
Generated from: task_80_festival_preparation_v1.yaml
Description: Festival Preparation - Quick Setup (Easier)
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
    Festival Preparation - Quick Setup (Easier)

    Primary objective: Cook 2x Cooked Shrimp, 1x Cooked Tuna, and craft 1x Silver Ring
    """
    inventories = get_final_inventories(traj_json)
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    cookedtuna_count = count_item_in_inventories(inventories, 'cookedtuna')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    alive = check_agents_alive(traj_json)

    passed = cookedshrimp_count >= 2 and cookedtuna_count >= 1 and silverring_count >= 1 and alive
    msg = f"cookedshrimp: {cookedshrimp_count}/2, cookedtuna: {cookedtuna_count}/1, silverring: {silverring_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_80_festival_preparation_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
