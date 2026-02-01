"""
Task 19 Farm Defense V2 Success Criteria Verifier
Generated from: task_19_farm_defense_v2.yaml
Description: Farm Defense Mission - Agricultural Team Protection (Harder)
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
    Farm Defense Mission - Agricultural Team Protection (Harder)

    Primary objective: Successfully protect collectors while they gather 16x corn and 8x tomato under agricultural threat conditions
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find corn_harvester_agent's inventory
    corn_harvester_items = {}
    for username, items in agent_items.items():
        if "corn_harvester" in username.lower():
            corn_harvester_items = items
            break
    corn_harvester_corn = corn_harvester_items.get("corn", 0)

    # Find tomato_gatherer_agent's inventory
    tomato_gatherer_items = {}
    for username, items in agent_items.items():
        if "tomato_gatherer" in username.lower():
            tomato_gatherer_items = items
            break
    tomato_gatherer_tomato = tomato_gatherer_items.get("tomato", 0)

    alive = check_agents_alive(traj_json)

    passed = corn_harvester_corn >= 16 and tomato_gatherer_tomato >= 8 and alive
    msg = f"corn(corn_harvester): {corn_harvester_corn}/16, tomato(tomato_gatherer): {tomato_gatherer_tomato}/8, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_19_farm_defense_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
