"""
Task 98 Mining Conglomerate V1 Success Criteria Verifier
Generated from: task_98_mining_conglomerate_v1.yaml
Description: Mining Conglomerate - Quick Forge (Easier)
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
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Mining Conglomerate - Quick Forge (Easier)

    Primary objective: Mine 4x ironore, 3x coal, smelt 3x ironbar, and craft 1x Heavy Sword
    """
    inventories = get_final_inventories(traj_json)
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    coal_count = count_item_in_inventories(inventories, 'coal')
    ironbar_count = count_item_in_inventories(inventories, 'ironbar')
    heavysword_count = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    alive = check_agents_alive(traj_json)

    passed = ironore_count >= 4 and coal_count >= 3 and ironbar_count >= 3 and heavysword_count >= 1 and alive
    msg = f"ironore: {ironore_count}/4, coal: {coal_count}/3, ironbar: {ironbar_count}/3, heavysword: {heavysword_count}/1, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_98_mining_conglomerate_v1_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
