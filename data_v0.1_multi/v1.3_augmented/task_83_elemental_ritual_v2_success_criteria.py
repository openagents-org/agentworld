"""
Task 83 Elemental Ritual V2 Success Criteria Verifier
Generated from: task_83_elemental_ritual_v2.yaml
Description: Elemental Ritual - Grand Ceremony (Harder)
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
    Elemental Ritual - Grand Ceremony (Harder)

    Primary objective: Craft 2x Beryl Pendant, 2x Gold Ring, and collect 10x blueberry
    """
    inventories = get_final_inventories(traj_json)
    berylpendant_count = count_item_in_inventories(inventories, 'berylpendant')
    goldring_count = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'goldenring')
    blueberry_count = count_item_in_inventories(inventories, 'blueberry')
    alive = check_agents_alive(traj_json)

    passed = berylpendant_count >= 2 and goldring_count >= 2 and blueberry_count >= 10 and alive
    msg = f"berylpendant: {berylpendant_count}/2, goldring: {goldring_count}/2, blueberry: {blueberry_count}/10, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_83_elemental_ritual_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
