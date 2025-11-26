"""
Task 38: Trade Network Operations Verification

Primary Objective: Successfully establish trade networks, coordinate commercial
activities, and develop profitable market operations

Success: All agents survive and complete within time limit (34 rounds)
- This is a coordination/soft-objective task
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


def task_38_verifier(traj_json):
    """
    Verify Task 38: Trade Network Operations
    - All agents survive
    - Complete within 34 rounds
    """
    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')

    # Check rounds
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 34

    print(f'Total rounds: {num_rounds}/34')

    passed = all_alive and within_limit

    print(f'\nChecks:')
    print(f'  All agents survive: {"PASSED" if all_alive else "FAILED"}')
    print(f'  Within 34 rounds: {"PASSED" if within_limit else "FAILED"}')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 38: Trade Network Operations")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_38_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
