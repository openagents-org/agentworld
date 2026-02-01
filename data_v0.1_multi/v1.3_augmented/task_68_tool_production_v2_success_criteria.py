"""
Task 68 Tool Production V2 Success Criteria Verifier
Generated from: task_68_tool_production_v2.yaml
Description: Tool Production - Master Smithy (Harder)
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
    Tool Production - Master Smithy (Harder)

    Primary objective: Mine ore, smelt bars, and craft 4x Pickaxe, 4x Axe, and 2x Heavy Sword
    """
    inventories = get_final_inventories(traj_json)
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')
    axe_count = count_item_in_inventories(inventories, 'axe')
    sword2_count = count_item_in_inventories(inventories, 'sword2')
    alive = check_agents_alive(traj_json)

    passed = pickaxe_count >= 4 and axe_count >= 4 and sword2_count >= 2 and alive
    msg = f"pickaxe: {pickaxe_count}/4, axe: {axe_count}/4, sword2: {sword2_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_68_tool_production_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
