"""
Task 22 Magical Defense V1 Success Criteria Verifier
Generated from: task_22_magical_defense_v1.yaml
Description: Magical Defense - Lightning Staff Forge & Ice Guardian Battle (Easier)
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
    Magical Defense - Lightning Staff Forge & Ice Guardian Battle (Easier)

    Primary objective: Craft a Magic Staff and defeat one Ice Wizard
    """
    inventories = get_final_inventories(traj_json)
    has_lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    alive = check_agents_alive(traj_json)

    passed = has_lightningstaff and alive
    msg = f"Lightning staff: {has_lightningstaff}, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_22_magical_defense_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
