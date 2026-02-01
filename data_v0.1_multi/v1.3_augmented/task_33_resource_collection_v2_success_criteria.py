"""
Task 33 Resource Collection V2 Success Criteria Verifier
Generated from: task_33_resource_collection_v2.yaml
Description: Resource Collection and Crafting - Coordinated Production (Harder)
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
    Resource Collection and Crafting - Coordinated Production (Harder)

    Primary objective: Craft 1x Axe and 1x Wooden Bow through specialized resource gathering and coordinated crafting
    """
    inventories = get_final_inventories(traj_json)
    axe_count = count_item_in_inventories(inventories, 'axe')
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')
    alive = check_agents_alive(traj_json)

    passed = axe_count >= 1 and woodenbow_count >= 1 and alive
    msg = f"Axe: {axe_count}/1, Wooden bow: {woodenbow_count}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_33_resource_collection_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
