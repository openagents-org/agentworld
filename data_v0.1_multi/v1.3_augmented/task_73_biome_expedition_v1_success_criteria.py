"""
Task 73 Biome Expedition V1 Success Criteria Verifier
Generated from: task_73_biome_expedition_v1.yaml
Description: Biome Expedition - Quick Hunt (Easier)
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
    Biome Expedition - Quick Hunt (Easier)

    Primary objective: Collect 3x logs, defeat 1x Goblin, and craft 1x Wooden Bow with provided materials
    """
    inventories = get_final_inventories(traj_json)
    logs_count = count_item_in_inventories(inventories, 'logs')
    woodenbow_count = count_item_in_inventories(inventories, 'woodenbow')

    # Combat targets: {'Goblin': 1}
    kills = count_combat_kills(traj_json, ['Goblin'])
    alive = check_agents_alive(traj_json)

    passed = logs_count >= 3 and woodenbow_count >= 1 and kills >= 1 and alive
    msg = f"logs: {logs_count}/3, woodenbow: {woodenbow_count}/1, kills: {kills}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_73_biome_expedition_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
