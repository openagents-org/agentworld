"""
Task 66 Archery Production V1 Success Criteria Verifier
Generated from: task_66_archery_production_v1.yaml
Description: Archery Production - Golden Bow (Easier)
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
    Archery Production - Golden Bow (Easier)

    Primary objective: Craft 1x Golden Bow and 10x Arrows with provided materials
    """
    inventories = get_final_inventories(traj_json)
    goldenbow_count = count_item_in_inventories(inventories, 'goldenbow')
    arrow_count = count_item_in_inventories(inventories, 'arrow')
    alive = check_agents_alive(traj_json)

    passed = goldenbow_count >= 1 and arrow_count >= 10 and alive
    msg = f"goldenbow: {goldenbow_count}/1, arrow: {arrow_count}/10, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_66_archery_production_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
