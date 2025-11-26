"""
Task 59: Elite Merchant Guild Verification

Primary Objective: Establish a 7-member merchant guild where each specialist gathers
unique resources, trades with peers, and collectively crafts 4x Golden items,
3x Staffs, and 2x Specialty weapons

Success (9 masterpiece items total):
- 4x Golden items (goldensword, goldenbow, goldenboots, goldring)
- 3x Elemental staffs (lightningstaff, firestaff, icestaff)
- 2x Specialty weapons (pickaxe, heavysword)
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


def task_59_verifier(traj_json):
    """
    Verify Task 59: Elite Merchant Guild
    - 4x Golden items
    - 3x Elemental staffs
    - 2x Specialty weapons
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Define item categories
    golden_items = ["goldensword", "goldenbow", "goldenboots", "goldring", "goldenring"]
    elemental_staffs = ["lightningstaff", "firestaff", "icestaff"]
    specialty_weapons = ["pickaxe", "heavysword", "sword2"]

    # Count items
    golden_count = 0
    staff_count = 0
    weapon_count = 0
    item_breakdown = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)

            if k in golden_items:
                golden_count += x
                item_breakdown[k] = item_breakdown.get(k, 0) + x
            elif k in elemental_staffs:
                staff_count += x
                item_breakdown[k] = item_breakdown.get(k, 0) + x
            elif k in specialty_weapons:
                weapon_count += x
                item_breakdown[k] = item_breakdown.get(k, 0) + x

    print(f'Golden items: {golden_count}')
    print(f'Elemental staffs: {staff_count}')
    print(f'Specialty weapons: {weapon_count}')
    print(f'Item breakdown: {item_breakdown}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Verification
    golden_passed = golden_count >= 4
    staff_passed = staff_count >= 3
    weapon_passed = weapon_count >= 2

    passed = golden_passed and staff_passed and weapon_passed

    print(f'\nChecks:')
    print(f'  Golden items >= 4: {"PASSED" if golden_passed else "FAILED"} ({golden_count}/4)')
    print(f'  Elemental staffs >= 3: {"PASSED" if staff_passed else "FAILED"} ({staff_count}/3)')
    print(f'  Specialty weapons >= 2: {"PASSED" if weapon_passed else "FAILED"} ({weapon_count}/2)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 59: Elite Merchant Guild")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_59_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
