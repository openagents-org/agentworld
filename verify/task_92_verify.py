"""
Task 92: Continental Trade Network Verification

Primary Objective: Establish a functioning continental trade network with 4
specialized trade hubs producing and exchanging goods across 50 rounds

Production Targets:
- Hub 1 (Forest): 30 logs, 20 sticks, 2 bows
- Hub 2 (Coastal): 20 cookedshrimp, 8 jellyfishsmoothie
- Hub 3 (Mountain): 15 ironbar, 8 goldbar, 3 gold rings
- Hub 4 (Forge): 2 heavy swords, 2 axes, 20 arrows

Success: Meet key production targets
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


def task_92_verifier(traj_json):
    """
    Verify Task 92: Continental Trade Network
    Key targets: cookedshrimp, ironbar, goldbar, goldring, heavysword, axe
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
    cookedshrimp = item_counts.get("cookedshrimp", 0)
    jellyfishsmoothie = item_counts.get("jellyfishsmoothie", 0)
    ironbar = item_counts.get("ironbar", 0)
    goldbar = item_counts.get("goldbar", 0)
    goldring = item_counts.get("goldring", 0)
    heavysword = item_counts.get("heavysword", 0) + item_counts.get("sword2", 0)
    axe = item_counts.get("axe", 0)

    print(f'Cooked Shrimp: {cookedshrimp}')
    print(f'Jellyfish Smoothie: {jellyfishsmoothie}')
    print(f'Iron Bars: {ironbar}')
    print(f'Gold Bars: {goldbar}')
    print(f'Gold Rings: {goldring}')
    print(f'Heavy Swords: {heavysword}')
    print(f'Axes: {axe}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Verification - key targets
    shrimp_passed = cookedshrimp >= 20
    smoothie_passed = jellyfishsmoothie >= 8
    iron_passed = ironbar >= 15
    gold_passed = goldbar >= 8
    ring_passed = goldring >= 3
    sword_passed = heavysword >= 2
    axe_passed = axe >= 2

    passed = (shrimp_passed and smoothie_passed and iron_passed and
              gold_passed and ring_passed and sword_passed and axe_passed)

    print(f'\nChecks:')
    print(f'  Cooked Shrimp >= 20: {"PASSED" if shrimp_passed else "FAILED"} ({cookedshrimp}/20)')
    print(f'  Jellyfish Smoothie >= 8: {"PASSED" if smoothie_passed else "FAILED"} ({jellyfishsmoothie}/8)')
    print(f'  Iron Bars >= 15: {"PASSED" if iron_passed else "FAILED"} ({ironbar}/15)')
    print(f'  Gold Bars >= 8: {"PASSED" if gold_passed else "FAILED"} ({goldbar}/8)')
    print(f'  Gold Rings >= 3: {"PASSED" if ring_passed else "FAILED"} ({goldring}/3)')
    print(f'  Heavy Swords >= 2: {"PASSED" if sword_passed else "FAILED"} ({heavysword}/2)')
    print(f'  Axes >= 2: {"PASSED" if axe_passed else "FAILED"} ({axe}/2)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 92: Continental Trade Network")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_92_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
