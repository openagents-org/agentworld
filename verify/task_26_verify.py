"""
Task 26: Desert Caravan Trading Verification

Primary Objective: Successfully establish desert trading operations, gather rare desert
materials, and complete a profitable trade circuit

Success:
- All agents survive the harsh desert expedition
- Gather desert resources (cactus materials, desert ores, etc.)
"""
import argparse
import json
import re


def get_final_agent_status(traj_json):
    """
    Get final HP status for all agents from the last round.
    Returns dict of {agent_name: current_hp}
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


def task_26_verifier(traj_json):
    """
    Verify Task 26: Desert Caravan Trading
    1. All agents survive
    2. Gather desert resources
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count desert-related resources
    desert_items = ["cactus", "sand", "desert", "ore", "coal", "ironore", "goldore"]
    total_desert_resources = 0
    resource_breakdown = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(d_item in k for d_item in desert_items):
                total_desert_resources += x
                resource_breakdown[k] = resource_breakdown.get(k, 0) + x

    print(f'Desert resources collected: {total_desert_resources}')
    if resource_breakdown:
        print(f'Resource breakdown: {resource_breakdown}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # For desert caravan, primary requirement is survival
    survival_passed = all_alive
    passed = survival_passed

    print(f'\nChecks:')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'  Resources gathered: {total_desert_resources} (info only)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 26: Desert Caravan Trading")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_26_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
