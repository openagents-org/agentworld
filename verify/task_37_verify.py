"""
Task 37: Survival Expedition Verification

Primary Objective: Successfully survive in challenging environments, manage limited
resources efficiently, and demonstrate environmental adaptation skills

Success:
- All agents survive challenging environmental conditions
- Resource management demonstrated
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


def task_37_verifier(traj_json):
    """
    Verify Task 37: Survival Expedition
    Primary: All agents survive
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count total resources for info
    total_resources = 0
    for items in inventory.values():
        for item in items:
            total_resources += item.get("count", 0)

    print(f'Total inventory items across all agents: {total_resources}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # For survival expedition, primary check is all agents survive
    survival_passed = all_alive
    passed = survival_passed

    print(f'\nChecks:')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 37: Survival Expedition")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_37_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
