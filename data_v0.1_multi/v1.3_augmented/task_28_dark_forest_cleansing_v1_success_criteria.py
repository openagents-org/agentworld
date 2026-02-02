"""
Task 28 Dark Forest Cleansing V1 Success Criteria Verifier
Generated from: task_28_dark_forest_cleansing_v1.yaml
Description: Dark Forest Cleansing - Dark Wolf Hunt (Easier)
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
    Dark Forest Cleansing - Dark Wolf Hunt (Easier)

    Primary objective: Successfully defeat the Dark Wolf boss and collect wolfarmor with enhanced starting resources
    """
    inventories = get_final_inventories(traj_json)

    # Check for wolfarmor drop - definitive proof of Dark Wolf kill
    wolfarmor = has_item_in_any_inventory(inventories, 'wolfarmor')

    # Check combat kills
    kills = count_combat_kills(traj_json, ['Dark Wolf', 'Wolf'])

    boss_killed = wolfarmor or kills >= 1
    alive = check_agents_alive(traj_json)

    passed = boss_killed and wolfarmor
    msg = f"Wolfarmor: {wolfarmor}, Kills: {kills}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_28_dark_forest_cleansing_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
