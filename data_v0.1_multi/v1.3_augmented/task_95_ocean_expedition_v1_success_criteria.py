"""
Task 95 Ocean Expedition V1 Success Criteria Verifier
Generated from: task_95_ocean_expedition_v1.yaml
Description: Ocean Expedition - Quick Voyage (Easier)
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
    Ocean Expedition - Quick Voyage (Easier)

    Primary objective: Catch 4x rawshrimp, defeat Mermaid at (580, 755), and cook 2x Cooked Shrimp
    """
    inventories = get_final_inventories(traj_json)
    rawshrimp_count = count_item_in_inventories(inventories, 'rawshrimp')
    cookedshrimp_count = count_item_in_inventories(inventories, 'cookedshrimp')
    alive = check_agents_alive(traj_json)

    passed = rawshrimp_count >= 4 and cookedshrimp_count >= 2 and alive
    msg = f"rawshrimp: {rawshrimp_count}/4, cookedshrimp: {cookedshrimp_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_95_ocean_expedition_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
