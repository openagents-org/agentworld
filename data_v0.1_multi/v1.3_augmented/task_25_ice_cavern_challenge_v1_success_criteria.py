"""
Task 25 Ice Cavern Challenge V1 Success Criteria Verifier
Generated from: task_25_ice_cavern_challenge_v1.yaml
Description: Ice Cavern Challenge - Frozen Tundra Survival (Easier)
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
    Ice Cavern Challenge - Frozen Tundra Survival (Easier)

    Primary objective: Successfully defeat one Ice Wizard and gather Ice Oak lumber with pre-gathered starting materials
    """
    inventories = get_final_inventories(traj_json)

    # Check for ice logs
    ice_items = ["iceoaklogs", "icelogs", "iceoak", "icelog"]
    total_ice_logs = 0
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(ice_key in k for ice_key in ice_items):
                total_ice_logs += x

    alive = check_agents_alive(traj_json)

    passed = total_ice_logs >= 1 and alive
    msg = f"Ice logs: {total_ice_logs}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_25_ice_cavern_challenge_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
