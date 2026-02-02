"""
Task 31 Woodworking Production V2 Success Criteria Verifier
Generated from: task_31_woodworking_production_v2.yaml
Description: Woodworking Production - Bow and Arrow Workshop (Harder)
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
    Woodworking Production - Bow and Arrow Workshop (Harder)

    Primary objective: Harvest 10x logs, craft 2x Wooden Bows, and produce 30x Arrows through coordinated woodworking
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')
    arrow_count = count_item_in_inventories(inventories, 'arrow')
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 10 and woodenbow_count >= 2 and arrow_count >= 30 and alive
    msg = f"logs: {logs_count}/10, woodenbow: {woodenbow_count}/2, arrow: {arrow_count}/30, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_31_woodworking_production_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
