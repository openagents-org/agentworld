"""
Task 74 Guild Equipment V2 Success Criteria Verifier
Generated from: task_74_guild_equipment_v2.yaml
Description: Guild Equipment - Full Arsenal (Harder)
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
    Guild Equipment - Full Arsenal (Harder)

    Primary objective: Craft 4x Heavy Sword, 2x Axe, 2x Wooden Bow, and 4x Silver Ring
    """
    inventories = get_final_inventories(traj_json)
    sword2_count = count_item_in_inventories(inventories, 'sword2')
    axe_count = count_item_in_inventories(inventories, 'axe')
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')
    silverring_count = count_item_in_inventories(inventories, 'silverring')
    alive = check_agents_alive(traj_json)

    passed = sword2_count >= 4 and axe_count >= 2 and woodenbow_count >= 2 and silverring_count >= 4 and alive
    msg = f"sword2: {sword2_count}/4, axe: {axe_count}/2, woodenbow: {woodenbow_count}/2, silverring: {silverring_count}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_74_guild_equipment_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
