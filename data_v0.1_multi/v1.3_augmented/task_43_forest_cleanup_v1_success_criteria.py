"""
Task 43 Forest Cleanup V1 Success Criteria Verifier
Generated from: task_43_forest_cleanup_v1.yaml
Description: Forest Cleanup - Rat Extermination (Easier)
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
    count_combat_kills,
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Forest Cleanup - Rat Extermination (Easier)

    Primary objective: Defeat 3x Rats and collect 3x blueberry with pre-gathered starting berries
    """
    inventories = get_final_inventories(traj_json)
    blueberry_count = count_item_in_inventories(inventories, 'blueberry')

    # Combat targets: {'Rat': 3}
    kills = count_combat_kills(traj_json, ['Rat'])
    alive = check_agents_alive(traj_json)

    passed = blueberry_count >= 3 and kills >= 3 and alive
    msg = f"blueberry: {blueberry_count}/3, kills: {kills}/3, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_43_forest_cleanup_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
