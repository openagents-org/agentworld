"""
Task 45 Caravan Escort V2 Success Criteria Verifier
Generated from: task_45_caravan_escort_v2.yaml
Description: Caravan Escort - Protected Gathering (Harder)
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
    Caravan Escort - Protected Gathering (Harder)

    Primary objective: Protect miner while they collect 6x goldnugget and defeat 4x hostile creatures
    """
    inventories = get_final_inventories(traj_json)
    goldnugget_count = count_item_in_inventories(inventories, 'goldnugget')
    alive = check_agents_alive(traj_json)

    passed = goldnugget_count >= 6 and alive
    msg = f"goldnugget: {goldnugget_count}/6, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_45_caravan_escort_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
