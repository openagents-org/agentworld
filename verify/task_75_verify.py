"""
Task 75: Continental Relief Convoy Verification

Primary Objective: Deliver consolidated medical and engineering supplies to the
coastal refugee pier after executing a four-phase convoy plan in 50-52 rounds

Success Criteria:
- Smelt 30+ iron bars
- Cook 30+ cookedshrimp
- Craft 60+ arrows
- All agents HP > 25% at the end
- Complete within 52 rounds
"""
import argparse
import json
import re


def get_final_agent_status(traj_json):
    """
    Get final HP status for all agents.
    Returns dict of {agent_name: {'current': hp, 'max': max_hp, 'percent': pct}}
    """
    agent_hp = {}
    if not traj_json.get('rounds'):
        return agent_hp

    last_round = traj_json['rounds'][-1]
    for act in last_round.get('actions', []):
        agent_name = act.get('agent_name', '')
        status = act.get('status', '')
        hp_match = re.search(r'❤️(\d+)/(\d+)', status)
        if hp_match:
            current = int(hp_match.group(1))
            max_hp = int(hp_match.group(2))
            percent = (current / max_hp * 100) if max_hp > 0 else 0
            agent_hp[agent_name] = {
                'current': current,
                'max': max_hp,
                'percent': percent
            }

    return agent_hp


def task_75_verifier(traj_json):
    """
    Verify Task 75: Continental Relief Convoy
    - 30+ iron bars
    - 30+ cooked shrimp
    - 60+ arrows
    - All agents HP > 25%
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

    ironbar = item_counts.get("ironbar", 0)
    cookedshrimp = item_counts.get("cookedshrimp", 0)
    arrow = item_counts.get("arrow", 0)

    print(f'Iron bars: {ironbar}')
    print(f'Cooked shrimp: {cookedshrimp}')
    print(f'Arrows: {arrow}')

    # Check agent HP
    agent_hp = get_final_agent_status(traj_json)
    all_healthy = True
    low_hp_agents = []

    print(f'\nAgent HP status:')
    for agent, hp_data in agent_hp.items():
        status_str = f"{hp_data['current']}/{hp_data['max']} ({hp_data['percent']:.1f}%)"
        print(f'  {agent}: {status_str}')
        if hp_data['percent'] <= 25:
            all_healthy = False
            low_hp_agents.append(agent)

    if low_hp_agents:
        print(f'\nAgents with HP <= 25%: {low_hp_agents}')

    # Check rounds
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 52

    print(f'\nTotal rounds: {num_rounds}/52')

    # Verification
    ironbar_passed = ironbar >= 30
    shrimp_passed = cookedshrimp >= 30
    arrow_passed = arrow >= 60
    hp_passed = all_healthy
    rounds_passed = within_limit

    passed = ironbar_passed and shrimp_passed and arrow_passed and hp_passed

    print(f'\nChecks:')
    print(f'  Iron bars >= 30: {"PASSED" if ironbar_passed else "FAILED"} ({ironbar}/30)')
    print(f'  Cooked shrimp >= 30: {"PASSED" if shrimp_passed else "FAILED"} ({cookedshrimp}/30)')
    print(f'  Arrows >= 60: {"PASSED" if arrow_passed else "FAILED"} ({arrow}/60)')
    print(f'  All agents HP > 25%: {"PASSED" if hp_passed else "FAILED"}')
    print(f'  Within 52 rounds: {"PASSED" if rounds_passed else "FAILED"} ({num_rounds}/52)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 75: Continental Relief Convoy")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_75_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
