"""
Task 80: Grand Festival Preparation Verification

Primary Objective: Prepare a complete festival celebration with diverse resources,
cooked dishes, competition prizes, and decorative items

Success Criteria:
- At least 10+ cooked food items for feast
- At least 4 competition prizes (3 silver rings + 1 golden ring)
- At least 3 decorative items (2 pendants + 1 staff)
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


def task_80_verifier(traj_json):
    """
    Verify Task 80: Grand Festival Preparation
    - 10+ cooked food items
    - 4+ prize rings (3 silver + 1 golden)
    - 3+ decorative items (pendants + staff)
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

    # Cooked food items
    cooked_food_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                        "cookedmeat", "jellyfishsmoothie", "stew"]
    cooked_food = sum(item_counts.get(k, 0) for k in cooked_food_keys)

    # Prize rings
    silver_rings = item_counts.get("silverring", 0)
    golden_rings = item_counts.get("goldring", 0) + item_counts.get("goldenring", 0)
    total_rings = silver_rings + golden_rings

    # Decorative items (pendants and staffs)
    pendant_keys = ["berylpendant", "topazpendant", "emeraldpendant", "pendant"]
    pendants = sum(item_counts.get(k, 0) for k in pendant_keys)
    staffs = item_counts.get("magicstaff", 0) + item_counts.get("staff", 0) + item_counts.get("lightningstaff", 0)
    decorations = pendants + staffs

    print(f'Cooked food items: {cooked_food}')
    print(f'  Breakdown: {[(k, item_counts.get(k, 0)) for k in cooked_food_keys if item_counts.get(k, 0) > 0]}')
    print(f'Prize rings: {total_rings} (silver: {silver_rings}, golden: {golden_rings})')
    print(f'Decorative items: {decorations} (pendants: {pendants}, staffs: {staffs})')
    print(f'\nAll items: {item_counts}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Check rounds
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 51

    print(f'Total rounds: {num_rounds}/51')

    # Verification
    food_passed = cooked_food >= 10
    rings_passed = total_rings >= 4
    decor_passed = decorations >= 3

    passed = food_passed and rings_passed and decor_passed

    print(f'\nChecks:')
    print(f'  Cooked food >= 10: {"PASSED" if food_passed else "FAILED"} ({cooked_food}/10)')
    print(f'  Prize rings >= 4: {"PASSED" if rings_passed else "FAILED"} ({total_rings}/4)')
    print(f'  Decorations >= 3: {"PASSED" if decor_passed else "FAILED"} ({decorations}/3)')
    print(f'  Within 51 rounds: {"PASSED" if within_limit else "FAILED"} ({num_rounds}/51)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 80: Grand Festival Preparation")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_80_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
