"""
Task 02 Arrow Production V1 Success Criteria Verifier
Generated from: task_02_arrow_production_v1.yaml
Description: Cooperative Arrow Production - Archer Supply Chain (Easier)
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
    Cooperative Arrow Production - Archer Supply Chain (Easier)

    Primary objective: Produce a batch of 10 arrows through coordinated material gathering and crafting
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find fletcher_agent's inventory
    fletcher_items = {}
    for username, items in agent_items.items():
        if "fletcher" in username.lower():
            fletcher_items = items
            break
    fletcher_arrows = fletcher_items.get("arrow", 0)

    passed = fletcher_arrows >= 10
    msg = f"arrows(fletcher): {fletcher_arrows}/10"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_02_arrow_production_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
