"""
Task 28 Dark Forest Cleansing V2 Success Criteria Verifier
Generated from: task_28_dark_forest_cleansing_v2.yaml
Description: Dark Forest Cleansing - Dark Wolf Hunt (Harder)
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
    count_combat_kills,
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Dark Forest Cleansing - Dark Wolf Hunt (Harder)

    Primary objective: Successfully defeat Dark Wolf, cleanse forest of additional threats, and harvest dark forest resources
    """
    inventories = get_final_inventories(traj_json)

    # Check for wolfarmor drop - definitive proof of Dark Wolf kill
    wolfarmor = has_item_in_any_inventory(inventories, 'wolfarmor')

    # Check combat kills (harder = more kills required)
    kills = count_combat_kills(traj_json, ['Dark Wolf', 'Wolf', 'Skeleton', 'Spider'])

    boss_killed = wolfarmor or kills >= 1
    alive = check_agents_alive(traj_json)

    # Harder version: need wolfarmor AND more kills AND survival
    passed = wolfarmor and kills >= 2 and alive
    msg = f"Wolfarmor: {wolfarmor}, Kills: {kills}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_28_dark_forest_cleansing_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
