"""
Task 53 Culinary Expedition V1 Success Criteria Verifier
Generated from: task_53_culinary_expedition_v1.yaml
Description: Culinary Expedition - Seafood Feast (Easier)
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
    Culinary Expedition - Seafood Feast (Easier)

    Primary objective: Cook 2x Cooked Shrimp and 1x Tuna Sushi with partial ingredients provided
    """
    inventories = get_final_inventories(traj_json)
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    tunasushi_count = count_item_in_inventories(inventories, 'tunasushi')
    alive = check_agents_alive(traj_json)

    passed = cookedshrimp_count >= 2 and tunasushi_count >= 1 and alive
    msg = f"cookedshrimp: {cookedshrimp_count}/2, tunasushi: {tunasushi_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_53_culinary_expedition_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
