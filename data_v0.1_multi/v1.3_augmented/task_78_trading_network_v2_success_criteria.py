"""
Task 78 Trading Network V2 Success Criteria Verifier
Generated from: task_78_trading_network_v2.yaml
Description: Trading Network - Full Trade Route (Harder)
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
    Trading Network - Full Trade Route (Harder)

    Primary objective: Collect 20x logs, 16x ironore, 12x goldnugget, and craft 2x Golden Ring and 2x Silver Ring
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    goldnugget_count = count_item_in_inventories(inventories, 'goldnugget')
    goldring_count = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 20 and ironore_count >= 16 and goldnugget_count >= 12 and goldring_count >= 2 and silverring_count >= 2 and alive
    msg = f"logs: {logs_count}/20, ironore: {ironore_count}/16, goldnugget: {goldnugget_count}/12, goldring: {goldring_count}/2, silverring: {silverring_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_78_trading_network_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
