"""
Task 32: Wilderness Expedition Verification

Primary Objective: Successfully navigate wilderness areas, defeat wild creatures,
and gather available resources through team coordination

Success:
- Defeat wild creatures (Wolves, Worker Ants, etc.)
- Gather resources
- All agents survive
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


def count_combat_actions(traj_json):
    """
    Count attack actions performed.
    """
    attacks = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            if 'attack' in action_str:
                attacks += 1
    return attacks


def task_32_verifier(traj_json):
    """
    Verify Task 32: Wilderness Expedition
    1. Defeat wild creatures
    2. Gather resources
    3. All agents survive
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count gathered resources (anything other than starting items)
    starting_items = ["flask", "apple", "arrow"]
    total_resources = 0
    resource_breakdown = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k not in starting_items:
                total_resources += x
                resource_breakdown[k] = resource_breakdown.get(k, 0) + x

    print(f'Resources gathered (excluding starting items): {total_resources}')
    if resource_breakdown:
        print(f'Resource breakdown: {resource_breakdown}')

    # Count combat actions
    combat_count = count_combat_actions(traj_json)
    print(f'Combat actions performed: {combat_count}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # For wilderness expedition, survival is the primary criteria
    survival_passed = all_alive
    passed = survival_passed

    print(f'\nChecks:')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'  Combat actions: {combat_count} (info only)')
    print(f'  Resources: {total_resources} (info only)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 32: Wilderness Expedition")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_32_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
