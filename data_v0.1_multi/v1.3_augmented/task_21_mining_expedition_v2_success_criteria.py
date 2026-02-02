"""
Task 21 Mining Expedition V2 Success Criteria Verifier
Generated from: task_21_mining_expedition_v2.yaml
Description: Deep Mining Expedition - Precious Metal Extraction (Harder)
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
    Deep Mining Expedition - Precious Metal Extraction (Harder)

    Primary objective: Successfully mine multiple gold ores and craft 2x golden rings through coordinated mining and advanced smithing
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find master_smith_agent's inventory
    master_smith_items = {}
    for username, items in agent_items.items():
        if "master_smith" in username.lower():
            master_smith_items = items
            break
    master_smith_goldring = master_smith_items.get("goldring", 0)

    passed = master_smith_goldring >= 2
    msg = f"goldring(master_smith): {master_smith_goldring}/2"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_21_mining_expedition_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
