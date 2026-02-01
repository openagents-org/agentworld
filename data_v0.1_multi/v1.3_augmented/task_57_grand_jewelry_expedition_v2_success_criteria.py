"""
Task 57 Grand Jewelry Expedition V2 Success Criteria Verifier
Generated from: task_57_grand_jewelry_expedition_v2.yaml
Description: Grand Jewelry Expedition (Harder)
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
    Grand Jewelry Expedition (Harder)

    Primary objective: Craft 3x Gold Rings and 4x Beryl Pendants with gathered materials
    """
    inventories = get_final_inventories(traj_json)
    goldring_count = count_item_in_inventories(inventories, 'goldring')
    berylpendant_count = count_item_in_inventories(inventories, 'berylpendant')
    alive = check_agents_alive(traj_json)

    passed = goldring_count >= 3 and berylpendant_count >= 4 and alive
    msg = f"goldring: {goldring_count}/3, berylpendant: {berylpendant_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_57_grand_jewelry_expedition_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
