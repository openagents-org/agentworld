"""
Task 39 Farming Harvest V2 Success Criteria Verifier
Generated from: task_39_farming_harvest_v2.yaml
Description: Farming Harvest - Crop Collection (Harder)
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
    Farming Harvest - Crop Collection (Harder)

    Primary objective: Harvest 8x corn, 8x tomato, 6x peach, and 4x blueberry from farming regions
    """
    inventories = get_final_inventories(traj_json)
    corn_count = count_item_in_inventories(inventories, 'corn')
    tomato_count = count_item_in_inventories(inventories, 'tomato')
    peach_count = count_item_in_inventories(inventories, 'peach')
    blueberry_count = count_item_in_inventories(inventories, 'blueberry')
    alive = check_agents_alive(traj_json)

    passed = corn_count >= 8 and tomato_count >= 8 and peach_count >= 6 and blueberry_count >= 4 and alive
    msg = f"corn: {corn_count}/8, tomato: {tomato_count}/8, peach: {peach_count}/6, blueberry: {blueberry_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_39_farming_harvest_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
