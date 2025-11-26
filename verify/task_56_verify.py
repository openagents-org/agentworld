"""
Task 56: Cross-Region Trading Network Verification

Primary Objective: Establish a cross-region trading network to gather resources
from 5 different biomes and craft 3x Golden Rings, 2x Lightning Staffs, and
1x Heavy Sword

Success:
- Craft 3x goldring
- Craft 2x lightningstaff
- Craft 1x heavysword
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


def task_56_verifier(traj_json):
    """
    Verify Task 56: Cross-Region Trading Network
    - 3x goldring
    - 2x lightningstaff
    - 1x heavysword (or sword2)
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count target items across all agents
    target_items = {
        "goldring": 0,
        "lightningstaff": 0,
        "heavysword": 0,
        "sword2": 0  # alternative name for heavy sword
    }

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in target_items:
                target_items[k] += x

    goldring = target_items["goldring"]
    lightningstaff = target_items["lightningstaff"]
    heavysword = target_items["heavysword"] + target_items["sword2"]

    print(f'Gold Rings: {goldring}')
    print(f'Lightning Staffs: {lightningstaff}')
    print(f'Heavy Swords: {heavysword}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Verification
    goldring_passed = goldring >= 3
    staff_passed = lightningstaff >= 2
    sword_passed = heavysword >= 1

    passed = goldring_passed and staff_passed and sword_passed

    print(f'\nChecks:')
    print(f'  Gold Rings >= 3: {"PASSED" if goldring_passed else "FAILED"} ({goldring}/3)')
    print(f'  Lightning Staffs >= 2: {"PASSED" if staff_passed else "FAILED"} ({lightningstaff}/2)')
    print(f'  Heavy Swords >= 1: {"PASSED" if sword_passed else "FAILED"} ({heavysword}/1)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 56: Cross-Region Trading Network")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_56_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
