"""
Task 29 Castle Siege V1 Success Criteria Verifier
Generated from: task_29_castle_siege_v1.yaml
Description: Castle Siege Warfare - Fortress Assault & Defense (Easier)
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
    Castle Siege Warfare - Fortress Assault & Defense (Easier)

    Primary objective: Successfully defeat Ice Knight commander with enhanced combat capabilities
    """
    # Check combat kills (Ice Knight)
    kills = count_combat_kills(traj_json, ['Ice Knight', 'IceKnight'])

    # Also check for ice-related loot as backup proof of kill
    inventories = get_final_inventories(traj_json)
    ice_loot = (has_item_in_any_inventory(inventories, 'icearmor') or
                has_item_in_any_inventory(inventories, 'iceshield') or
                has_item_in_any_inventory(inventories, 'icesword'))

    boss_killed = kills >= 1 or ice_loot
    alive = check_agents_alive(traj_json)

    passed = boss_killed
    msg = f"Kills: {kills}/1, Ice loot: {ice_loot}, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_29_castle_siege_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
