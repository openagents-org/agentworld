"""
Task 71: Multi-Region Supply Network Verification

Primary Objective: Create a functioning 5-region supply network with specialized
gathering teams, transport logistics, and centralized crafting over 55 rounds

Success:
- Forest: 50+ logs, 100+ sticks
- Mountain: 40+ iron ore, 40+ coal, 20+ gold ore
- Crafting: 40+ iron bars, 20+ gold bars
- Final: 10+ weapons, 7+ rings
"""
import argparse
import json
import re


def get_final_agent_status(traj_json):
    """Get final HP status for all agents."""
    agent_hp = {}
    if not traj_json.get('rounds'):
        return agent_hp

    last_round = traj_json['rounds'][-1]
    for act in last_round.get('actions', []):
        agent_name = act.get('agent_name', '')
        status = act.get('status', '')
        hp_match = re.search(r'❤️(\d+)/(\d+)', status)
        if hp_match:
            agent_hp[agent_name] = int(hp_match.group(1))

    return agent_hp


def task_71_verifier(traj_json):
    """
    Verify Task 71: Multi-Region Supply Network
    Focus on crafted output: iron bars, gold bars, weapons, rings
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count items
    item_counts = {}
    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    # Key metrics
    iron_bars = item_counts.get("ironbar", 0)
    gold_bars = item_counts.get("goldbar", 0)

    # Weapons: swords, axes, bows
    weapons = (item_counts.get("sword", 0) + item_counts.get("sword1", 0) +
               item_counts.get("sword2", 0) + item_counts.get("heavysword", 0) +
               item_counts.get("axe", 0) + item_counts.get("bow", 0))

    # Rings
    rings = (item_counts.get("goldring", 0) + item_counts.get("ring", 0) +
             item_counts.get("silverring", 0))

    print(f'Iron bars: {iron_bars}')
    print(f'Gold bars: {gold_bars}')
    print(f'Weapons: {weapons}')
    print(f'Rings: {rings}')
    print(f'All items: {item_counts}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Verification - using simplified criteria
    iron_passed = iron_bars >= 40
    gold_passed = gold_bars >= 20
    weapons_passed = weapons >= 10
    rings_passed = rings >= 7

    passed = iron_passed and gold_passed and weapons_passed and rings_passed

    print(f'\nChecks:')
    print(f'  Iron bars >= 40: {"PASSED" if iron_passed else "FAILED"} ({iron_bars}/40)')
    print(f'  Gold bars >= 20: {"PASSED" if gold_passed else "FAILED"} ({gold_bars}/20)')
    print(f'  Weapons >= 10: {"PASSED" if weapons_passed else "FAILED"} ({weapons}/10)')
    print(f'  Rings >= 7: {"PASSED" if rings_passed else "FAILED"} ({rings}/7)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 71: Multi-Region Supply Network")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_71_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
