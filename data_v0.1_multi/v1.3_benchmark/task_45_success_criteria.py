"""
Task 45 Success Criteria Verifier
Auto-extracted from task_verifier.py

Updated 2026-01-28: Fixed to use agent keys (agent_1, agent_2, agent_3) instead of 
usernames, and corrected item key from 'goldore' to 'goldnugget'.

Note: The game has TWO items both named "Gold Ore":
- 'goldnugget': Obtained from mining Gold Rock (this is what agents can actually get)
- 'goldore': Exists in items.json but has NO acquisition path (orphaned item)
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


def get_agent_items_by_key(traj_json: Dict) -> Dict[str, Dict[str, int]]:
    """Get final inventory item counts keyed by agent key (agent_1, agent_2, etc.).
    
    This is more reliable than using usernames which can vary between task runs.
    """
    inventory = {}
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            agent_key = act.get('agent_name')  # "agent_1", "agent_2", "agent_3"
            if agent_key and 'observation' in act and 'inventory' in act['observation']:
                inventory[agent_key] = act['observation']['inventory'].get('items', [])
    
    agent_items = {}
    for agent_key, items in inventory.items():
        item_counts = {}
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x
        agent_items[agent_key] = item_counts
    
    return agent_items


def task_45_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Caravan Escort - agent_3 (miner) must have 3+ gold ore, 2+ kills, all survive.
    
    Uses agent keys instead of usernames for reliability across different task configurations.
    Uses 'goldnugget' item key (the actual mineable gold ore) instead of 'goldore' (orphaned item).
    """
    # Check agent_3 (miner) inventory for gold ore
    # Note: agent_3 is the miner in task 45's configuration
    agent_items = get_agent_items_by_key(traj_json)
    miner_items = agent_items.get('agent_3', {})
    
    # Use 'goldnugget' - the actual item obtained from mining Gold Rock
    # (not 'goldore' which is an orphaned item with no acquisition path)
    goldore = miner_items.get('goldnugget', 0)
    has_goldore = goldore >= 3

    # Check combat kills (by guards)
    # Pass None to count ALL hostile mob kills (mobs like Spectre, Dark Mage, Iron Ogre, etc.)
    # The old pattern ['hostile', 'creature', 'enemy', 'monster'] didn't match actual mob names
    kills = count_combat_kills(traj_json, None)
    has_kills = kills >= 2

    # Check all agents alive
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    passed = has_goldore and has_kills and all_alive
    msg = f"Miner gold ore: {goldore}/3, Kills: {kills}/2, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def task_45_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 57
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/57"
    return (1 if passed else 0, msg)


def task_45_verifier_v2(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 77
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/77"
    return (1 if passed else 0, msg)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 45."""
    return task_45_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_45_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
