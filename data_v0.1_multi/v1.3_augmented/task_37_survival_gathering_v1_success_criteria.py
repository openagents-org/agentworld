"""
Task 37 Survival Gathering V1 Success Criteria Verifier
Generated from: task_37_survival_gathering_v1.yaml
Description: Survival Gathering - Food and Resource Collection (Easier)
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
    Survival Gathering - Food and Resource Collection (Easier)

    Primary objective: Collect 3x blueberry, 2x corn, and 2x logs with pre-gathered starting materials
    """
    inventories = get_final_inventories(traj_json)
    blueberry_count = count_item_in_inventories(inventories, 'blueberry')
    corn_count = count_item_in_inventories(inventories, 'corn')
    logs_count = count_item_in_inventories(inventories, 'logs')
    alive = check_agents_alive(traj_json)

    passed = blueberry_count >= 3 and corn_count >= 2 and logs_count >= 2 and alive
    msg = f"blueberry: {blueberry_count}/3, corn: {corn_count}/2, logs: {logs_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_37_survival_gathering_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
