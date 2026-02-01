"""
Task 44 Messenger Run V2 Success Criteria Verifier
Generated from: task_44_messenger_run_v2.yaml
Description: Messenger Run - Resource Delivery (Harder)
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
    Messenger Run - Resource Delivery (Harder)

    Primary objective: Gather 6x logs, 4x coal, and 3x ironore - deliver all to coordinator
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    coal_count = count_item_in_inventories(inventories, 'coal')
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 6 and coal_count >= 4 and ironore_count >= 3 and alive
    msg = f"logs: {logs_count}/6, coal: {coal_count}/4, ironore: {ironore_count}/3, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_44_messenger_run_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
