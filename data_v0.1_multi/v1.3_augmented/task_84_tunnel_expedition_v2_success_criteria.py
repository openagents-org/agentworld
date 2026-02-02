"""
Task 84 Tunnel Expedition V2 Success Criteria Verifier
Generated from: task_84_tunnel_expedition_v2.yaml
Description: Tunnel Expedition - Deep Dive (Harder)
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
    count_combat_kills,
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    Tunnel Expedition - Deep Dive (Harder)

    Primary objective: Mine 12x ironore, 10x coal, defeat 5x Skeletons, and craft 2x Pickaxe
    """
    inventories = get_final_inventories(traj_json)
    ironore_count = count_item_in_inventories(inventories, 'ironore')
    coal_count = count_item_in_inventories(inventories, 'coal')
    pickaxe_count = count_item_in_inventories(inventories, 'pickaxe')

    # Combat targets: {'Skeleton': 5}
    kills = count_combat_kills(traj_json, ['Skeleton'])
    alive = check_agents_alive(traj_json)

    passed = ironore_count >= 12 and coal_count >= 10 and pickaxe_count >= 2 and kills >= 5 and alive
    msg = f"ironore: {ironore_count}/12, coal: {coal_count}/10, pickaxe: {pickaxe_count}/2, kills: {kills}/5, alive: {alive}"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_84_tunnel_expedition_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
