"""
Task 51 Survival Challenge V2 Success Criteria Verifier
Generated from: task_51_survival_challenge_v2.yaml
Description: Survival Challenge - Equipment Preparation (Harder)
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
    Survival Challenge - Equipment Preparation (Harder)

    Primary objective: Craft 2x Wooden Bow, 2x Axe, and collect 10x rawshrimp and 8x logs
    """
    inventories = get_final_inventories(traj_json)
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')
    axe_count = count_item_in_inventories(inventories, 'axe')
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    logs_count = count_item_in_inventories(inventories, 'logs')
    alive = check_agents_alive(traj_json)

    passed = woodenbow_count >= 2 and axe_count >= 2 and rawshrimp_count >= 10 and logs_count >= 8 and alive
    msg = f"woodenbow: {woodenbow_count}/2, axe: {axe_count}/2, rawshrimp: {rawshrimp_count}/10, logs: {logs_count}/8, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_51_survival_challenge_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
