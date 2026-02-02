"""
Task 86 Forge Vanguard V2 Success Criteria Verifier
Generated from: task_86_forge_vanguard_v2.yaml
Description: Forge Vanguard - Full Arsenal (Harder)
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
    Forge Vanguard - Full Arsenal (Harder)

    Primary objective: Mine 15x ironore, 12x coal, smelt 10x ironbar, and craft 4x Heavy Sword and 2x Axe
    """
    inventories = get_final_inventories(traj_json)
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    coal_count = count_item_in_inventories(inventories, 'coal')
    ironbar_count = count_item_in_inventories(inventories, 'ironbar')
    heavysword_count = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    axe_count = count_item_in_inventories(inventories, 'axe')
    alive = check_agents_alive(traj_json)

    passed = ironore_count >= 15 and coal_count >= 12 and ironbar_count >= 10 and heavysword_count >= 4 and axe_count >= 2 and alive
    msg = f"ironore: {ironore_count}/15, coal: {coal_count}/12, ironbar: {ironbar_count}/10, heavysword: {heavysword_count}/4, axe: {axe_count}/2, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_86_forge_vanguard_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
