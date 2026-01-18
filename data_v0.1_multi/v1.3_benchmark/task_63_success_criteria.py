"""
Task 63 Success Criteria Verifier
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


def task_63_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Enchanted Jewelry Workshop.
    YAML criteria:
    - Team inventory contains 2x goldring
    - Team inventory contains 2x silverring
    - Team inventory contains 2x berylpendant
    - All agents survive the crafting mission
    """
    inventories = get_final_inventories(traj_json)

    goldring = count_item_in_inventories(inventories, 'goldring')
    silverring = count_item_in_inventories(inventories, 'silverring')
    berylpendant = count_item_in_inventories(inventories, 'berylpendant')

    alive = check_agents_alive(traj_json)

    gold_ok = goldring >= 2
    silver_ok = silverring >= 2
    beryl_ok = berylpendant >= 2

    success = gold_ok and silver_ok and beryl_ok and alive
    msg = f"Goldring: {goldring}/2, Silverring: {silverring}/2, Berylpendant: {berylpendant}/2, All alive: {alive}"
    return (1 if success else 0, msg)


def task_63_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    counts = aggregate_item_counts(inventories)
    ring_keys = ["silverring", "goldring", "goldenring", "topazring", "rubyring", "ruby_ring"]
    pendant_keys = ["berylpendant", "emeraldpendant", "topazpendant", "rubypendant"]
    base_item_keys = ["beryl", "emerald", "ruby", "topaz", "sapphire"]
    rings = sum(counts.get(k, 0) for k in ring_keys)
    pendants = sum(counts.get(k, 0) for k in pendant_keys)
    base_items = sum(counts.get(k, 0) for k in base_item_keys)
    total = rings + pendants + base_items
    success = rings >= 5 and pendants >= 5 and base_items >= 5 and total >= 15
    msg = (f"Rings: {rings}/5, Pendants: {pendants}/5, Base items: {base_items}/5, "
           f"Total: {total}/15")
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 63."""
    return task_63_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_63_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
