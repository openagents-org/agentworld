"""
Task 15 Jellyfish Smoothie V2 Success Criteria Verifier
Generated from: task_15_jellyfish_smoothie_v2.yaml
Description: Cooperative Jellyfish Smoothie - Exotic Beverage Creation (Harder)
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
    Cooperative Jellyfish Smoothie - Exotic Beverage Creation (Harder)

    Primary objective: Create THREE jellyfish smoothies through coordinated fishing, container crafting, and cooking
    """
    inventories = get_final_inventories(traj_json)
    jellyfishsmoothie_count = count_item_in_inventories(inventories, 'jellyfishsmoothie')

    passed = jellyfishsmoothie_count >= 3
    msg = f"Jellyfish smoothies: {jellyfishsmoothie_count}/3"
    return (1 if passed else 0, msg)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python task_15_jellyfish_smoothie_v2_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
