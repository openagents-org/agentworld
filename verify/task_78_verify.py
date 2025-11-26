"""
Task 78: Transcontinental Trading Network Verification

Primary Objective: Establish a transcontinental trading network where 10 agents
gather region-specific resources, travel to consolidation hubs, exchange materials,
and craft 5 different items requiring materials from 6+ regions

Required Crafts:
- Golden Bow (goldbar + logs)
- Beryl Pendant (berylgem + logs)
- Golden Ring (goldbar)
- Silver Ring (ironbar)
- Magic Staff (logs + beads)
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


def task_78_verifier(traj_json):
    """
    Verify Task 78: Transcontinental Trading Network
    Must craft 5 items:
    - Golden Bow
    - Beryl Pendant
    - Golden Ring
    - Silver Ring
    - Magic Staff
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count target items
    target_items = {
        "goldenbow": 0,
        "berylpendant": 0,
        "pendant": 0,  # alternative name
        "goldring": 0,
        "goldenring": 0,  # alternative
        "silverring": 0,
        "magicstaff": 0,
        "staff": 0  # might be base staff
    }

    all_items = {}
    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            all_items[k] = all_items.get(k, 0) + x
            if k in target_items:
                target_items[k] += x

    # Calculate totals
    golden_bow = target_items["goldenbow"]
    beryl_pendant = target_items["berylpendant"] + target_items["pendant"]
    golden_ring = target_items["goldring"] + target_items["goldenring"]
    silver_ring = target_items["silverring"]
    magic_staff = target_items["magicstaff"]

    print(f'Golden Bow: {golden_bow}')
    print(f'Beryl Pendant: {beryl_pendant}')
    print(f'Golden Ring: {golden_ring}')
    print(f'Silver Ring: {silver_ring}')
    print(f'Magic Staff: {magic_staff}')
    print(f'\nAll items: {all_items}')

    # Count how many of the 5 target items were crafted
    crafted_count = 0
    if golden_bow >= 1:
        crafted_count += 1
    if beryl_pendant >= 1:
        crafted_count += 1
    if golden_ring >= 1:
        crafted_count += 1
    if silver_ring >= 1:
        crafted_count += 1
    if magic_staff >= 1:
        crafted_count += 1

    print(f'\nItems crafted: {crafted_count}/5')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'All agents alive: {all_alive}')

    # Verification - need all 5 items
    bow_passed = golden_bow >= 1
    pendant_passed = beryl_pendant >= 1
    goldring_passed = golden_ring >= 1
    silverring_passed = silver_ring >= 1
    staff_passed = magic_staff >= 1

    passed = bow_passed and pendant_passed and goldring_passed and silverring_passed and staff_passed

    print(f'\nChecks:')
    print(f'  Golden Bow >= 1: {"PASSED" if bow_passed else "FAILED"} ({golden_bow})')
    print(f'  Beryl Pendant >= 1: {"PASSED" if pendant_passed else "FAILED"} ({beryl_pendant})')
    print(f'  Golden Ring >= 1: {"PASSED" if goldring_passed else "FAILED"} ({golden_ring})')
    print(f'  Silver Ring >= 1: {"PASSED" if silverring_passed else "FAILED"} ({silver_ring})')
    print(f'  Magic Staff >= 1: {"PASSED" if staff_passed else "FAILED"} ({magic_staff})')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 78: Transcontinental Trading Network")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_78_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
