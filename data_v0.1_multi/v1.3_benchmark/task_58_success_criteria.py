"""
Task 58 Success Criteria Verifier
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


def task_58_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest Festival - cook 3x Corn Stew, craft 2x Silver Rings, and 1x Wooden Bow."""
    inventories = get_final_inventories(traj_json)
    
    # Check for stew (corn stew is 'stew' item)
    stew = count_item_in_inventories(inventories, 'stew') + count_item_in_inventories(inventories, 'stew2')
    silverring = count_item_in_inventories(inventories, 'silverring')
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')
    
    has_stew = stew >= 3
    has_rings = silverring >= 2
    has_bow = woodenbow >= 1
    
    # Check all agents alive
    alive = check_agents_alive(traj_json)
    
    passed = has_stew and has_rings and has_bow and alive
    msg = f"Corn Stew: {stew}/3, Silver Rings: {silverring}/2, Wooden Bow: {woodenbow}/1, All alive: {alive}"
    return (1 if passed else 0, msg)


def task_58_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    counts = aggregate_item_counts(inventories)

    cooked_food_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                        "cookedmeat", "jellyfishsmoothie", "stew", "stew2"]
    jewelry_keys = ["silverring", "goldring", "goldenring", "topazring", "berylpendant",
                    "emeraldpendant", "rubyring", "ruby_ring", "topazpendant"]
    tool_keys = ["pickaxe", "axe", "bow", "goldenbow", "fishingpole", "fishingrod",
                 "sword", "sword1", "sword2", "heavysword"]
    resource_keys = ["logs", "oak", "palm", "ice", "coal", "ironore", "goldore",
                     "rawshrimp", "rawtuna", "jellyfish", "crab", "fish", "herb",
                     "apple", "peach", "blueberry", "corn", "tomato", "cactus",
                     "feather", "string", "bead"]

    cooked_food = sum(counts.get(k, 0) for k in cooked_food_keys)
    jewelry = sum(counts.get(k, 0) for k in jewelry_keys)
    tools = sum(counts.get(k, 0) for k in tool_keys)
    resources = sum(counts.get(k, 0) for k in resource_keys)

    success = cooked_food >= 6 and jewelry >= 4 and tools >= 2 and resources >= 50
    msg = (f"Cooked dishes: {cooked_food}/6, Jewelry: {jewelry}/4, "
           f"Tools: {tools}/2, Resources: {resources}/50")
    return (1 if success else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 58."""
    return task_58_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_58_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
