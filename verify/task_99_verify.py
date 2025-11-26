"""
Task 99: Kingdom Festival Celebration Verification

Primary Objective: Successfully prepare and execute kingdom festival with 4 exhibition
arenas, 60+ prepared items, and coordinated performances within 60 rounds

Success Criteria:
- Culinary Guild: 30+ cooked dishes
- Artisans Guild: 20+ masterwork items (weapons, jewelry, tools)
- Total: 60+ festival items (food + crafts + combat trophies)
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


def task_99_verifier(traj_json):
    """
    Verify Task 99: Kingdom Festival Celebration
    - 30+ cooked dishes
    - 20+ masterwork items
    - 60+ total items
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count items by category
    item_counts = {}
    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    # Starting items to exclude
    starting_items = ["flask", "apple", "leatherarmor", "leatherboots", "ironarmor",
                      "ironboots", "platearmor", "coal", "string", "topaz", "manaflask",
                      "healthpotion", "arrow"]

    # Cooked dishes
    cooked_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                   "cookedmeat", "jellyfishsmoothie", "stew"]
    cooked_count = sum(item_counts.get(k, 0) for k in cooked_keys)

    # Masterwork items (weapons, jewelry, tools)
    masterwork_keys = ["heavysword", "sword2", "axe", "pickaxe", "bow",
                       "goldring", "goldenring", "silverring",
                       "emeraldpendant", "berylpendant", "topazpendant", "pendant",
                       "magicstaff", "lightningstaff"]
    masterwork_count = sum(item_counts.get(k, 0) for k in masterwork_keys)

    # Combat trophies (mob drops) - items not in starting or crafted categories
    trophy_keys = ["feather", "bead", "lightningbead", "emerald", "ruby", "beryl",
                   "rawmeat", "rawchicken", "rawbeef"]
    trophy_count = sum(item_counts.get(k, 0) for k in trophy_keys)

    # Total festival items (excluding starting items)
    total_festival = cooked_count + masterwork_count + trophy_count

    print(f'Cooked dishes: {cooked_count}')
    print(f'  Breakdown: {[(k, item_counts.get(k, 0)) for k in cooked_keys if item_counts.get(k, 0) > 0]}')
    print(f'Masterwork items: {masterwork_count}')
    print(f'  Breakdown: {[(k, item_counts.get(k, 0)) for k in masterwork_keys if item_counts.get(k, 0) > 0]}')
    print(f'Combat trophies: {trophy_count}')
    print(f'Total festival items: {total_festival}')
    print(f'\nAll items: {item_counts}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Check rounds
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 60

    print(f'Total rounds: {num_rounds}/60')

    # Verification
    food_passed = cooked_count >= 30
    masterwork_passed = masterwork_count >= 20
    total_passed = total_festival >= 60

    passed = food_passed and masterwork_passed and total_passed

    print(f'\nChecks:')
    print(f'  Cooked dishes >= 30: {"PASSED" if food_passed else "FAILED"} ({cooked_count}/30)')
    print(f'  Masterwork items >= 20: {"PASSED" if masterwork_passed else "FAILED"} ({masterwork_count}/20)')
    print(f'  Total items >= 60: {"PASSED" if total_passed else "FAILED"} ({total_festival}/60)')
    print(f'  Within 60 rounds: {"PASSED" if within_limit else "FAILED"} ({num_rounds}/60)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 99: Kingdom Festival Celebration")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_99_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
