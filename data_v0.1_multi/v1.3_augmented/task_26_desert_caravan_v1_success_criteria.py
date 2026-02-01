"""
Task 26 Desert Caravan V1 Success Criteria Verifier
Generated from: task_26_desert_caravan_v1.yaml
Description: Desert Caravan Expedition - Resource Gathering and Team Exchange (Easier)
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
    count_chat_messages,
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Desert Caravan Expedition - Resource Gathering and Team Exchange (Easier)

    Primary objective: Successfully reach the desert region and complete resource exchanges with pre-gathered materials
    """
    inventories = get_final_inventories(traj_json)

    # Check for mined ores
    ores = ['ironore', 'goldnugget', 'coal', 'copperore', 'tinore']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)

    # Check combat kills
    kills = count_combat_kills(traj_json, ['Cactus', 'Scorpion', 'Skeleton', 'Guardian'])

    # Check chat messages
    chat_count = count_chat_messages(traj_json)

    alive = check_agents_alive(traj_json)

    passed = ore_count >= 1 and kills >= 1 and chat_count >= 2 and alive
    msg = f"Ore: {ore_count}/1, Kills: {kills}/1, Chat: {chat_count}/2, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_26_desert_caravan_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
