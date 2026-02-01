"""
Task 09 Topaz Ring V1 Success Criteria Verifier
Generated from: task_09_topaz_ring_v1.yaml
Description: Cooperative Topaz Ring Crafting - Luxury Jewelry (Easier)
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
    Cooperative Topaz Ring Crafting - Luxury Jewelry (Easier)

    Primary objective: Create a topaz ring by combining topaz gem with gold ring base
    """
    inventories = get_final_inventories(traj_json)
    has_topazring = has_item_in_any_inventory(inventories, 'topazring')

    passed = has_topazring
    msg = f"Topaz ring: {has_topazring}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_09_topaz_ring_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
