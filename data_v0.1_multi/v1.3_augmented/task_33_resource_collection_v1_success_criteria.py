"""
Task 33 Resource Collection V1 Success Criteria Verifier
Generated from: task_33_resource_collection_v1.yaml
Description: Resource Collection - Multi-Material Gathering (Easier)
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
    Resource Collection - Multi-Material Gathering (Easier)

    Primary objective: Collect 3x logs, 2x coal, and 1x copperore with pre-gathered starting materials
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    coal_count = count_item_in_inventories(inventories, 'coal')
    copperore_count = count_item_in_inventories(inventories, 'copperore')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 3 and coal_count >= 2 and copperore_count >= 1 and alive
    msg = f"logs: {logs_count}/3, coal: {coal_count}/2, copperore: {copperore_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_33_resource_collection_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
