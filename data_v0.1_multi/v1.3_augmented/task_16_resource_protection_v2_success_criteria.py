"""
Task 16 Resource Protection V2 Success Criteria Verifier
Generated from: task_16_resource_protection_v2.yaml
Description: Resource Protection Mission - Guardian Team Defense (Harder)
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
    Resource Protection Mission - Guardian Team Defense (Harder)

    Primary objective: Successfully protect collectors while they gather 10x logs and 6x blueberry under combat conditions
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find lumber_collector_agent's inventory
    lumber_collector_items = {}
    for username, items in agent_items.items():
        if "lumber_collector" in username.lower():
            lumber_collector_items = items
            break
    lumber_collector_logs = lumber_collector_items.get("logs", 0)

    # Find forager_collector_agent's inventory
    forager_collector_items = {}
    for username, items in agent_items.items():
        if "forager_collector" in username.lower():
            forager_collector_items = items
            break
    forager_collector_blueberry = forager_collector_items.get("blueberry", 0)

    alive = check_agents_alive(traj_json)

    passed = lumber_collector_logs >= 10 and forager_collector_blueberry >= 6 and alive
    msg = f"logs(lumber_collector): {lumber_collector_logs}/10, blueberry(forager_collector): {forager_collector_blueberry}/6, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_16_resource_protection_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
