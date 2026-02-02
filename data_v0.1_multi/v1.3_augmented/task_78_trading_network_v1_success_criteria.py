"""
Task 78 Trading Network V1 Success Criteria Verifier
Generated from: task_78_trading_network_v1.yaml
Description: Trading Network - Quick Trade (Easier)
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
    Trading Network - Quick Trade (Easier)

    Primary objective: Collect 5x logs, 4x ironore, 3x goldnugget, and craft 1x Golden Ring
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    goldnugget_count = count_item_in_inventories(inventories, 'goldnugget')
    goldring_count = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 5 and ironore_count >= 4 and goldnugget_count >= 3 and goldring_count >= 1 and alive
    msg = f"logs: {logs_count}/5, ironore: {ironore_count}/4, goldnugget: {goldnugget_count}/3, goldring: {goldring_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_78_trading_network_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
