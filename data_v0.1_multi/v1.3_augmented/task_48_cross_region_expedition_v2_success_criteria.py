"""
Task 48 Cross Region Expedition V2 Success Criteria Verifier
Generated from: task_48_cross_region_expedition_v2.yaml
Description: Cross-Region Expedition - Multi-Biome Gathering (Harder)
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
    Cross-Region Expedition - Multi-Biome Gathering (Harder)

    Primary objective: Collect 10x logs, 8x coal, 6x rawshrimp from three biomes
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    coal_count = count_item_in_inventories(inventories, 'coal')
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 10 and coal_count >= 8 and rawshrimp_count >= 6 and alive
    msg = f"logs: {logs_count}/10, coal: {coal_count}/8, rawshrimp: {rawshrimp_count}/6, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_48_cross_region_expedition_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
