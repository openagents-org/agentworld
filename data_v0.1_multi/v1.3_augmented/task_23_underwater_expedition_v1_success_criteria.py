"""
Task 23 Underwater Expedition V1 Success Criteria Verifier
Generated from: task_23_underwater_expedition_v1.yaml
Description: Underwater Expedition - Deep Sea Treasure Hunt (Easier)
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
    get_agent_items_by_username,
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Underwater Expedition - Deep Sea Treasure Hunt (Easier)

    Primary objective: Successfully explore underwater regions and harvest 4x jellyfish with pre-gathered starting supplies
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find marine_harvester_agent's inventory
    marine_harvester_items = {}
    for username, items in agent_items.items():
        if "marine_harvester" in username.lower():
            marine_harvester_items = items
            break
    marine_harvester_jellyfish = marine_harvester_items.get("jellyfish", 0)

    alive = check_agents_alive(traj_json)

    passed = marine_harvester_jellyfish >= 4 and alive
    msg = f"jellyfish(marine_harvester): {marine_harvester_jellyfish}/4, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_23_underwater_expedition_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
