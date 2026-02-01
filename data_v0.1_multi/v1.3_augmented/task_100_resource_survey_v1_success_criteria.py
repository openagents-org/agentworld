"""
Task 100 Resource Survey V1 Success Criteria Verifier
Generated from: task_100_resource_survey_v1.yaml
Description: Resource Survey - Quick Survey (Easier)
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
    Resource Survey - Quick Survey (Easier)

    Primary objective: Collect 4x logs, 4x ironore, 3x icelogs, and 2x rawshrimp from different regions
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    icelogs_count = count_item_in_inventories(inventories, 'icelogs')
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 4 and ironore_count >= 4 and icelogs_count >= 3 and rawshrimp_count >= 2 and alive
    msg = f"logs: {logs_count}/4, ironore: {ironore_count}/4, icelogs: {icelogs_count}/3, rawshrimp: {rawshrimp_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_100_resource_survey_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
