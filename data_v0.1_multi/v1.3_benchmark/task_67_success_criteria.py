"""
Task 67 Success Criteria Verifier
Auto-extracted from task_verifier.py
"""

from typing import Dict, Tuple
from verifier_utils import (
    get_final_inventories,
    aggregate_item_counts,
    get_all_inventories,
    count_item_in_inventories,
    has_item_in_any_inventory,
    check_agents_alive,
    get_final_hp,
    get_final_agent_status,
    get_final_agent_hp_simple,
    count_combat_kills,
    count_attack_actions,
    count_crafted_items,
    check_crafted_items,
    count_chat_messages,
    get_agent_items_by_username,
)


def task_67_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Biome Resource Caravan - 80+ resources, 12+ crafted items."""
    inventories = get_final_inventories(traj_json)
    
    resource_keys = ["logs", "oak", "palm", "ice", "stick", "coal", "ironore", "goldore",
                     "rawshrimp", "rawtuna", "jellyfish", "crab", "fish", "herb", "apple",
                     "peach", "blueberry", "corn", "tomato", "cactus", "feather", "string", "bead"]
    crafted_keys = ["ironbar", "goldbar", "sword", "axe", "pickaxe", "bow", "arrow",
                    "cookedshrimp", "cookedtuna", "ring", "staff", "armor", "boots"]
    starting_items = ["flask", "apple"]

    total_resources = 0
    total_crafted = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in starting_items:
                continue
            is_resource = any(res in k for res in resource_keys)
            is_crafted = any(craft in k for craft in crafted_keys)
            if is_resource:
                total_resources += x
            elif is_crafted:
                total_crafted += x

    resources_passed = total_resources >= 80
    crafted_passed = total_crafted >= 12

    passed = resources_passed and crafted_passed
    msg = f"Resources: {total_resources}/80, Crafted: {total_crafted}/12"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 67."""
    return task_67_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_67_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
