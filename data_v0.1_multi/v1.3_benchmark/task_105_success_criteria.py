"""
Task 105 Success Criteria Verifier
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


def task_105_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Legendary Golden Tribute - 5 golden bows, 1 golden sword, all survive."""
    inventories = get_final_inventories(traj_json)

    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    goldenbow = item_counts.get("goldenbow", 0)
    goldensword = item_counts.get("goldensword", 0)

    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    bow_passed = goldenbow >= 5
    sword_passed = goldensword >= 1
    survival_passed = all_alive

    passed = bow_passed and sword_passed and survival_passed
    msg = f"Golden bows: {goldenbow}/5, Golden swords: {goldensword}/1, All alive: {all_alive}"
    return (1 if passed else 0, msg)


# =============================================================================
# VERSIONED OVERRIDES (v1/v2)
# =============================================================================


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 105."""
    return task_105_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_105_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
