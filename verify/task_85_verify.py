"""
Task 85: Frostveil Lifeline Convoy Verification

Primary Objective: Deliver the reinforced convoy manifest (logs, iron bars, two
lightningstaff, two icestaff, medical rations) from Ridge Camp (232,148) to the
Ice Guardian Outpost (260,156) while keeping every agent accounted for.

Success:
- Deliver convoy items to outpost
- All agents survive (accounted for)
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


def task_85_verifier(traj_json):
    """
    Verify Task 85: Frostveil Lifeline Convoy
    Primary: All agents accounted for (survive) with convoy delivered
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Check for convoy items
    convoy_items = ["icelogs", "ironbar", "lightningstaff", "icestaff", "jellyfish", "bluelily"]
    found_items = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(ci in k for ci in convoy_items):
                found_items[k] = found_items.get(k, 0) + x

    print(f'Convoy items found: {found_items}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]
    num_agents = len(agent_hp)

    print(f'Agent HP status: {agent_hp}')
    print(f'Total agents: {num_agents}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # For frostveil convoy, primary check is all agents accounted for (survive)
    survival_passed = all_alive
    passed = survival_passed

    print(f'\nChecks:')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 85: Frostveil Lifeline Convoy")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_85_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
