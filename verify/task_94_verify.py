"""
Task 94: Grand Maritime Trading Empire Verification

Primary Objective: Establish a fully operational maritime trading empire with
3 fishing fleets, 50+ trade goods, and active commerce routes within 60 rounds

Success Criteria:
- Fishing Fleet: 30+ seafood items (shrimp, jellyfish, crab)
- Shipyard: 20+ tools/weapons crafted (axes, swords, pickaxes)
- Trade Goods: 30+ luxury items (jewelry, cooked food, staves)
- Total Production: 80+ items across all divisions
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


def task_94_verifier(traj_json):
    """
    Verify Task 94: Grand Maritime Trading Empire
    - 30+ seafood
    - 20+ tools/weapons
    - 30+ luxury items
    - 80+ total
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Define categories
    seafood_keys = ["rawshrimp", "shrimp", "jellyfish", "crab", "rawtuna", "tuna", "fish"]
    tool_weapon_keys = ["axe", "sword", "pickaxe", "bow", "arrow", "heavysword", "sword1", "sword2"]
    luxury_keys = ["ring", "goldring", "silverring", "pendant", "staff", "cookedshrimp",
                   "cookedtuna", "jellyfishsmoothie", "emerald", "ruby", "bead"]

    # Count items
    seafood_count = 0
    tool_count = 0
    luxury_count = 0
    starting_items = ["flask", "apple", "leatherarmor", "leatherboots"]

    item_counts = {}
    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)

            if k in starting_items:
                continue

            item_counts[k] = item_counts.get(k, 0) + x

            if any(sf in k for sf in seafood_keys):
                seafood_count += x
            elif any(tw in k for tw in tool_weapon_keys):
                tool_count += x
            elif any(lx in k for lx in luxury_keys):
                luxury_count += x

    total = seafood_count + tool_count + luxury_count

    print(f'Seafood items: {seafood_count}')
    print(f'Tools/Weapons: {tool_count}')
    print(f'Luxury items: {luxury_count}')
    print(f'Total production: {total}')
    print(f'\nItem breakdown: {item_counts}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Verification
    seafood_passed = seafood_count >= 30
    tool_passed = tool_count >= 20
    luxury_passed = luxury_count >= 30
    total_passed = total >= 80

    passed = seafood_passed and tool_passed and luxury_passed and total_passed

    print(f'\nChecks:')
    print(f'  Seafood >= 30: {"PASSED" if seafood_passed else "FAILED"} ({seafood_count}/30)')
    print(f'  Tools/Weapons >= 20: {"PASSED" if tool_passed else "FAILED"} ({tool_count}/20)')
    print(f'  Luxury items >= 30: {"PASSED" if luxury_passed else "FAILED"} ({luxury_count}/30)')
    print(f'  Total >= 80: {"PASSED" if total_passed else "FAILED"} ({total}/80)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 94: Grand Maritime Trading Empire")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_94_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
