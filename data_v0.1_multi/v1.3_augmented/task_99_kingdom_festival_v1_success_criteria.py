"""
Task 99 Kingdom Festival V1 Success Criteria Verifier
Generated from: task_99_kingdom_festival_v1.yaml
Description: Kingdom Festival - Quick Prep (Easier)
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
    Kingdom Festival - Quick Prep (Easier)

    Primary objective: Defeat Ancient Wizard at (163, 339), cook 2x Cooked Shrimp, and craft 1x Heavy Sword and 1x Gold Ring
    """
    inventories = get_final_inventories(traj_json)
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    heavysword_count = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    goldring_count = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    alive = check_agents_alive(traj_json)

    passed = cookedshrimp_count >= 2 and heavysword_count >= 1 and goldring_count >= 1 and alive
    msg = f"cookedshrimp: {cookedshrimp_count}/2, heavysword: {heavysword_count}/1, goldring: {goldring_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_99_kingdom_festival_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
