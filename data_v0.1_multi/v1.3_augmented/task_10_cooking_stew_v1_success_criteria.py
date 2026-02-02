"""
Task 10 Cooking Stew V1 Success Criteria Verifier
Generated from: task_10_cooking_stew_v1.yaml
Description: Cooperative Stew Cooking - Culinary Team Production (Easier)
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
    Cooperative Stew Cooking - Culinary Team Production (Easier)

    Primary objective: Prepare a delicious stew through coordinated ingredient gathering and cooking
    """
    inventories = get_final_inventories(traj_json)
    has_stew = has_item_in_any_inventory(inventories, 'stew2') or has_item_in_any_inventory(inventories, 'stew')

    passed = has_stew
    msg = f"Stew: {has_stew}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_10_cooking_stew_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
