"""
Task 06 Heavy Sword V1 Success Criteria Verifier
Generated from: task_06_heavy_sword_v1.yaml
Description: Cooperative Heavy Sword Forging - Warrior Weapon Crafting (Easier)
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
    Cooperative Heavy Sword Forging - Warrior Weapon Crafting (Easier)

    Primary objective: Forge a heavy sword through coordinated material processing and weapon smithing
    """
    inventories = get_final_inventories(traj_json)
    has_heavysword = has_item_in_any_inventory(inventories, 'sword2') or has_item_in_any_inventory(inventories, 'heavysword')

    passed = has_heavysword
    msg = f"Heavy sword: {has_heavysword}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_06_heavy_sword_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
