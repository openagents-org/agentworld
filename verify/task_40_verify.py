"""
Task 40: Medical Emergency Response Verification

Primary Objective: Successfully establish emergency medical operations, coordinate
healthcare services, and provide effective life support assistance

Success:
- All agents survive (demonstrating successful medical operations)
- Coordination demonstrated through chat/actions
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


def count_chat_messages(traj_json):
    """Count chat/coordination messages."""
    chat_count = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            if 'chat' in action_str:
                chat_count += 1
    return chat_count


def task_40_verifier(traj_json):
    """
    Verify Task 40: Medical Emergency Response
    Primary: All agents survive with coordinated medical operations
    """
    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # Check coordination (chat messages)
    chat_count = count_chat_messages(traj_json)
    print(f'Chat/coordination messages: {chat_count}')

    # For medical emergency, primary check is all agents survive
    survival_passed = all_alive
    passed = survival_passed

    print(f'\nChecks:')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'  Coordination (chat): {chat_count} messages (info only)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 40: Medical Emergency Response")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_40_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
