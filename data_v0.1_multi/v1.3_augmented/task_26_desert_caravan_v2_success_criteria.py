"""
Task 26 Desert Caravan V2 Success Criteria Verifier
Generated from: task_26_desert_caravan_v2.yaml
Description: Desert Caravan Expedition - Resource Gathering and Team Exchange (Harder)
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
    Desert Caravan Expedition - Resource Gathering and Team Exchange (Harder)

    Primary objective: Successfully gather desert resources through mining and combat, defeat multiple desert creatures, and complete at least 5 resource exchanges
    """
    inventories = get_final_inventories(traj_json)

    # Check for mined ores
    ores = ['ironore', 'goldnugget', 'coal', 'copperore', 'tinore']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)

    # Check combat kills (harder = more kills)
    kills = count_combat_kills(traj_json, ['Cactus', 'Scorpion', 'Skeleton', 'Guardian'])

    # Check chat messages (harder = more coordination)
    chat_count = count_chat_messages(traj_json)

    alive = check_agents_alive(traj_json)

    passed = ore_count >= 2 and kills >= 2 and chat_count >= 5 and alive
    msg = f"Ore: {ore_count}/2, Kills: {kills}/2, Chat: {chat_count}/5, All alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_26_desert_caravan_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
