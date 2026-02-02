"""
Task 05 Beryl Pendant V1 Success Criteria Verifier
Generated from: task_05_beryl_pendant_v1.yaml
Description: Cooperative Beryl Pendant Crafting - Elegant Jewelry (Easier)
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
    Cooperative Beryl Pendant Crafting - Elegant Jewelry (Easier)

    Primary objective: Create a beryl pendant by combining beryl gem with crafted string
    """
    inventories = get_final_inventories(traj_json)
    has_berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')

    passed = has_berylpendant
    msg = f"Beryl pendant: {has_berylpendant}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_05_beryl_pendant_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
