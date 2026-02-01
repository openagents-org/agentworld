"""
Task 20 Orchard Protection V2 Success Criteria Verifier
Generated from: task_20_orchard_protection_v2.yaml
Description: Orchard Protection Mission - Fruit Grove Team Defense (Harder)
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
    Orchard Protection Mission - Fruit Grove Team Defense (Harder)

    Primary objective: Successfully protect collectors while they gather 12x blueberry and 6x rawtuna under orchard threat conditions
    """
    agent_items = get_agent_items_by_username(traj_json)

    # Find berry_picker_agent's inventory
    berry_picker_items = {}
    for username, items in agent_items.items():
        if "berry_picker" in username.lower():
            berry_picker_items = items
            break
    berry_picker_blueberry = berry_picker_items.get("blueberry", 0)

    # Find pond_fisher_agent's inventory
    pond_fisher_items = {}
    for username, items in agent_items.items():
        if "pond_fisher" in username.lower():
            pond_fisher_items = items
            break
    pond_fisher_rawtuna = pond_fisher_items.get("rawtuna", 0)

    alive = check_agents_alive(traj_json)

    passed = berry_picker_blueberry >= 12 and pond_fisher_rawtuna >= 6 and alive
    msg = f"blueberry(berry_picker): {berry_picker_blueberry}/12, rawtuna(pond_fisher): {pond_fisher_rawtuna}/6, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_20_orchard_protection_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
