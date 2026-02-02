"""
Task 43 Forest Cleanup V2 Success Criteria Verifier
Generated from: task_43_forest_cleanup_v2.yaml
Description: Forest Cleanup - Rat Extermination (Harder)
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
    Forest Cleanup - Rat Extermination (Harder)

    Primary objective: Defeat 10x Rats and collect 8x blueberry from the forest
    """
    inventories = get_final_inventories(traj_json)
    blueberry_count = count_item_in_inventories(inventories, 'blueberry')

    # Combat targets: {'Rat': 10}
    kills = count_combat_kills(traj_json, ['Rat'])
    alive = check_agents_alive(traj_json)

    passed = blueberry_count >= 8 and kills >= 10 and alive
    msg = f"blueberry: {blueberry_count}/8, kills: {kills}/10, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_43_forest_cleanup_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
