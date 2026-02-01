"""
Task 08 Bronze Alloy V2 Success Criteria Verifier
Generated from: task_08_bronze_alloy_v2.yaml
Description: Cooperative Bronze Alloy Creation - Advanced Metallurgy (Harder)
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
    Cooperative Bronze Alloy Creation - Advanced Metallurgy (Harder)

    Primary objective: Create FIVE bronze bars through coordinated copper and tin mining with challenging alloy smelting
    """
    inventories = get_final_inventories(traj_json)
    bronzebar_count = count_item_in_inventories(inventories, 'bronzebar')

    passed = bronzebar_count >= 5
    msg = f"bronzebar: {bronzebar_count}/5"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_08_bronze_alloy_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
