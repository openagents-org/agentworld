"""
Task 41 Tool Production V1 Success Criteria Verifier
Generated from: task_41_tool_production_v1.yaml
Description: Tool Production - Pickaxe and Axe Crafting (Easier)
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
    Tool Production - Pickaxe and Axe Crafting (Easier)

    Primary objective: Craft 1x Pickaxe using pre-gathered iron bars and logs
    """
    inventories = get_final_inventories(traj_json)
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    alive = check_agents_alive(traj_json)

    passed = pickaxe_count >= 1 and alive
    msg = f"pickaxe: {pickaxe_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_41_tool_production_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
