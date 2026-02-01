"""
Task 67 Resource Caravan V2 Success Criteria Verifier
Generated from: task_67_resource_caravan_v2.yaml
Description: Resource Caravan - Extended Expedition (Harder)
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
    Resource Caravan - Extended Expedition (Harder)

    Primary objective: Collect 12x logs, 10x coal, and craft 2x Pickaxe and 1x Axe
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    coal_count = count_item_in_inventories(inventories, 'coal')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    axe_count = count_item_in_inventories(inventories, 'axe')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 12 and coal_count >= 10 and pickaxe_count >= 2 and axe_count >= 1 and alive
    msg = f"logs: {logs_count}/12, coal: {coal_count}/10, pickaxe: {pickaxe_count}/2, axe: {axe_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_67_resource_caravan_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
