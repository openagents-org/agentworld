"""
Task 17 Forest Gathering V1 Success Criteria Verifier
Generated from: task_17_forest_gathering_v1.yaml
Description: Forest Gathering Mission - Wilderness Team Protection (Easier)
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
    Forest Gathering Mission - Wilderness Team Protection (Easier)

    Primary objective: Successfully protect collectors while they gather 2x palmlogs and 3x peach under wildlife threat conditions
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find palm_logger_agent's inventory
    palm_logger_items = {}
    for username, items in agent_items.items():
        if "palm_logger" in username.lower():
            palm_logger_items = items
            break
    palm_logger_palmlogs = palm_logger_items.get("palmlogs", 0)

    # Find peach_forager_agent's inventory
    peach_forager_items = {}
    for username, items in agent_items.items():
        if "peach_forager" in username.lower():
            peach_forager_items = items
            break
    peach_forager_peach = peach_forager_items.get("peach", 0)

    alive = check_agents_alive(traj_json)

    passed = palm_logger_palmlogs >= 2 and peach_forager_peach >= 3 and alive
    msg = f"palmlogs(palm_logger): {palm_logger_palmlogs}/2, peach(peach_forager): {peach_forager_peach}/3, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_17_forest_gathering_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
