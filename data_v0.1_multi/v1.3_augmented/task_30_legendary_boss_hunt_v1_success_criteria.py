"""
Task 30 Legendary Boss Hunt V1 Success Criteria Verifier
Generated from: task_30_legendary_boss_hunt_v1.yaml
Description: Legendary Boss Hunt - Triple Boss Elimination (Easier)
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
    Legendary Boss Hunt - Triple Boss Elimination (Easier)

    Primary objective: Defeat the Mermaid at (580, 755) and Dark Wolf at (1016, 682) with enhanced combat capabilities
    """
    # Combat targets: {'Mermaid': 1, 'Dark Wolf': 1}
    kills = count_combat_kills(traj_json, ['Mermaid', 'Dark Wolf'])
    alive = check_agents_alive(traj_json)

    passed = kills >= 2 and alive
    msg = f"kills: {kills}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_30_legendary_boss_hunt_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
