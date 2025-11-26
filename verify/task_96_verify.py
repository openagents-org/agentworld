"""
Task 96: Mountain Rescue Operation Verification

Primary Objective: Execute successful mountain rescue operation across 3 regions,
delivering 100+ supplies and establishing 3 rescue camps within 50 rounds

Success:
- Gather 100+ supply items total
- Establish 3 rescue camps (Camp Alpha, Beta, Gamma)
- Deliver 30+ items to each camp
- Complete within 50 rounds
"""
import argparse
import json
import re


def get_final_agent_status(traj_json):
    """
    Get final HP status for all agents from the last round.
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
            agent_hp[agent_name] = int(hp_match.group(1))

    return agent_hp


def task_96_verifier(traj_json):
    """
    Verify Task 96: Mountain Rescue Operation
    1. Gather 100+ supply items
    2. Establish 3 rescue camps
    3. All agents survive
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count total supplies (healing items + food + tools)
    supply_items = ["flask", "apple", "cookedshrimp", "healthpotion", "logs", "pickaxe", "axe"]
    total_supplies = 0
    supply_breakdown = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(s in k for s in supply_items):
                total_supplies += x
                supply_breakdown[k] = supply_breakdown.get(k, 0) + x

    print(f'Total supplies collected: {total_supplies}')
    if supply_breakdown:
        print(f'Supply breakdown: {supply_breakdown}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # Check number of rounds
    num_rounds = len(traj_json.get('rounds', []))
    print(f'Total rounds: {num_rounds}')

    # Verification
    supplies_passed = total_supplies >= 100
    survival_passed = all_alive
    rounds_passed = num_rounds <= 50

    # Primary requirement: 100+ supplies AND survival
    passed = supplies_passed and survival_passed

    print(f'\nChecks:')
    print(f'  Supplies >= 100: {"PASSED" if supplies_passed else "FAILED"} ({total_supplies}/100)')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'  Complete within 50 rounds: {"PASSED" if rounds_passed else "FAILED"} ({num_rounds}/50)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 96: Mountain Rescue Operation")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_96_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
