"""
Task 18 Coastal Harvest V2 Success Criteria Verifier
Generated from: task_18_coastal_harvest_v2.yaml
Description: Coastal Harvest Mission - Seaside Team Protection (Harder)
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
    Coastal Harvest Mission - Seaside Team Protection (Harder)

    Primary objective: Successfully protect collectors while they gather 12x rawshrimp and 6x icelogs under coastal threat conditions
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find shrimp_fisher_agent's inventory
    shrimp_fisher_items = {}
    for username, items in agent_items.items():
        if "shrimp_fisher" in username.lower():
            shrimp_fisher_items = items
            break
    shrimp_fisher_rawshrimp = shrimp_fisher_items.get("rawshrimp", 0)

    # Find ice_logger_agent's inventory
    ice_logger_items = {}
    for username, items in agent_items.items():
        if "ice_logger" in username.lower():
            ice_logger_items = items
            break
    ice_logger_icelogs = ice_logger_items.get("icelogs", 0)

    alive = check_agents_alive(traj_json)

    passed = shrimp_fisher_rawshrimp >= 12 and ice_logger_icelogs >= 6 and alive
    msg = f"rawshrimp(shrimp_fisher): {shrimp_fisher_rawshrimp}/12, icelogs(ice_logger): {ice_logger_icelogs}/6, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_18_coastal_harvest_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
