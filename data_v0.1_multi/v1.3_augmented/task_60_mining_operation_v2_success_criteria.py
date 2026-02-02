"""
Task 60 Mining Operation V2 Success Criteria Verifier
Generated from: task_60_mining_operation_v2.yaml
Description: Mining Operation - Ore Extraction (Harder)
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
    Mining Operation - Ore Extraction (Harder)

    Primary objective: Mine ore, smelt 12x ironbar, and craft 2x Pickaxe and 4x Silver Ring
    """
    inventories = get_final_inventories(traj_json)
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    alive = check_agents_alive(traj_json)

    passed = pickaxe_count >= 2 and silverring_count >= 4 and alive
    msg = f"pickaxe: {pickaxe_count}/2, silverring: {silverring_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_60_mining_operation_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
