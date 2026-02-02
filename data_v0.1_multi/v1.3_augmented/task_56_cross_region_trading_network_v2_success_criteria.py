"""
Task 56 Cross Region Trading Network V2 Success Criteria Verifier
Generated from: task_56_cross_region_trading_network_v2.yaml
Description: Cross-Region Trading Network (Harder)
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
    Cross-Region Trading Network (Harder)

    Primary objective: Craft 6x Silver Rings, 4x Axes, and 2x Heavy Swords through full production chain
    """
    inventories = get_final_inventories(traj_json)
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    axe_count = count_item_in_inventories(inventories, 'axe')
    sword2_count = count_item_in_inventories(inventories, 'sword2')
    alive = check_agents_alive(traj_json)

    passed = silverring_count >= 6 and axe_count >= 4 and sword2_count >= 2 and alive
    msg = f"silverring: {silverring_count}/6, axe: {axe_count}/4, sword2: {sword2_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_56_cross_region_trading_network_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
