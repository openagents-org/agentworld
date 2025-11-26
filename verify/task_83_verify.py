"""
Task 83: Elemental Relay Ritual Verification

Primary Objective: Deliver four elemental cores to the Central Obelisk

Core Recipes:
- Earth core: berylpendant (beryl + string)
- Flame core: goldring (goldbar)
- Tide core: cookedtuna + lightningbead (focus item)
- Gale core: lightningstaff (staff upgrade)

Success: All 4 cores crafted and delivered
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


def task_83_verifier(traj_json):
    """
    Verify Task 83: Elemental Relay Ritual
    Must have all 4 elemental cores:
    - Earth core: berylpendant
    - Flame core: goldring
    - Tide core: cookedtuna (with lightningbead as focus)
    - Gale core: lightningstaff
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

    # Core items
    berylpendant = item_counts.get("berylpendant", 0)
    goldring = item_counts.get("goldring", 0) + item_counts.get("goldenring", 0)
    cookedtuna = item_counts.get("cookedtuna", 0)
    lightningbead = item_counts.get("lightningbead", 0)
    lightningstaff = item_counts.get("lightningstaff", 0)

    print(f'Earth Core (berylpendant): {berylpendant}')
    print(f'Flame Core (goldring): {goldring}')
    print(f'Tide Core (cookedtuna): {cookedtuna}')
    print(f'  Tide Focus (lightningbead): {lightningbead}')
    print(f'Gale Core (lightningstaff): {lightningstaff}')
    print(f'\nAll items: {item_counts}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Check rounds
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 52

    print(f'Total rounds: {num_rounds}/52')

    # Verification - need all 4 cores
    earth_passed = berylpendant >= 1
    flame_passed = goldring >= 1
    tide_passed = cookedtuna >= 1  # lightningbead is optional focus
    gale_passed = lightningstaff >= 1

    passed = earth_passed and flame_passed and tide_passed and gale_passed

    print(f'\nChecks:')
    print(f'  Earth Core (berylpendant >= 1): {"PASSED" if earth_passed else "FAILED"} ({berylpendant})')
    print(f'  Flame Core (goldring >= 1): {"PASSED" if flame_passed else "FAILED"} ({goldring})')
    print(f'  Tide Core (cookedtuna >= 1): {"PASSED" if tide_passed else "FAILED"} ({cookedtuna})')
    print(f'  Gale Core (lightningstaff >= 1): {"PASSED" if gale_passed else "FAILED"} ({lightningstaff})')
    print(f'  Within 52 rounds: {"PASSED" if within_limit else "FAILED"} ({num_rounds}/52)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 83: Elemental Relay Ritual")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_83_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
