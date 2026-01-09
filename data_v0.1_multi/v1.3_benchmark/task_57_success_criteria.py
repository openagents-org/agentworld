"""
Task 57 Success Criteria Verifier
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


def task_57_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Jewelry Expedition."""
    inventories = get_final_inventories(traj_json)
    gems = ['beryl', 'topaz', 'emerald', 'ruby', 'sapphire']
    gem_count = sum(count_item_in_inventories(inventories, g) for g in gems)
    jewelry = ['silverring', 'goldring', 'topazring', 'berylpendant']
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))
    success = gem_count >= 5 or jewelry_count >= 2
    msg = f"Gems: {gem_count}, Jewelry: {jewelry_count}"
    return (1 if success else 0, msg)


def task_57_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    counts = aggregate_item_counts(inventories)
    ruby_rings = counts.get("rubyring", 0) + counts.get("ruby_ring", 0)
    emerald_pendants = counts.get("emeraldpendant", 0)
    topaz_rings = counts.get("topazring", 0)
    beryl_pendants = counts.get("berylpendant", 0)
    success = (ruby_rings >= 3 and emerald_pendants >= 2 and
               topaz_rings >= 1 and beryl_pendants >= 2)
    msg = (f"Ruby rings: {ruby_rings}/3, Emerald pendants: {emerald_pendants}/2, "
           f"Topaz rings: {topaz_rings}/1, Beryl pendants: {beryl_pendants}/2")
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 57."""
    return task_57_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_57_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
