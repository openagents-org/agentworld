"""
Task 13 Bucket Crafting V1 Success Criteria Verifier
Generated from: task_13_bucket_crafting_v1.yaml
Description: Wooden Bow Workshop - Cooperative Crafting (Easier)
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
    Wooden Bow Workshop - Cooperative Crafting (Easier)

    Primary objective: Craft 1x Wooden Bow through coordinated wood harvesting and string production
    """
    inventories = get_final_inventories(traj_json)
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')

    passed = woodenbow_count >= 1
    msg = f"woodenbow: {woodenbow_count}/1"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_13_bucket_crafting_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
