"""
Task 07 Pickaxe Crafting V2 Success Criteria Verifier
Generated from: task_07_pickaxe_crafting_v2.yaml
Description: Cooperative Pickaxe Crafting - Mining Tool Production (Harder)
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
    Cooperative Pickaxe Crafting - Mining Tool Production (Harder)

    Primary objective: Forge TWO high-quality pickaxes through coordinated large-scale material extraction and tool smithing
    """
    inventories = get_final_inventories(traj_json)
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')

    passed = pickaxe_count >= 2
    msg = f"Pickaxes: {pickaxe_count}/2"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_07_pickaxe_crafting_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
