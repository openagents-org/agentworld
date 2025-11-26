"""
Task 20: Orchard Protection Verification

Primary Objective: Successfully protect collectors while they gather 6x blueberry
and 3x rawtuna under orchard threat conditions

Success:
- berry_picker_agent has at least 6x blueberry in inventory
- pond_fisher_agent has at least 3x rawtuna in inventory
"""
import argparse
import json


def task_20_verifier(traj_json):
    """
    Verify Task 20: Orchard Protection
    Check if berry_picker_agent has 6+ blueberry and pond_fisher_agent has 3+ rawtuna
    """
    # Get agent username mapping from task definition
    task_def = traj_json.get('task_definition', {})
    agent_usernames = {}
    for key, value in task_def.items():
        if key.startswith('agent_') and isinstance(value, dict):
            agent_usernames[key] = value.get('username', key)

    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count items per agent
    agent_items = {}
    for agent_key, items in inventory.items():
        username = agent_usernames.get(agent_key, agent_key)
        item_counts = {}
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x
        agent_items[username] = item_counts

    # Check berry_picker_agent for blueberry
    berry_picker_items = {}
    for username, items in agent_items.items():
        if "berry_picker" in username.lower():
            berry_picker_items = items
            break

    # Check pond_fisher_agent for rawtuna
    pond_fisher_items = {}
    for username, items in agent_items.items():
        if "pond_fisher" in username.lower():
            pond_fisher_items = items
            break

    blueberry = berry_picker_items.get("blueberry", 0)
    rawtuna = pond_fisher_items.get("rawtuna", 0)

    print(f'berry_picker_agent blueberry: {blueberry}')
    print(f'pond_fisher_agent rawtuna: {rawtuna}')

    berry_passed = blueberry >= 6
    tuna_passed = rawtuna >= 3
    passed = berry_passed and tuna_passed

    print(f'\nChecks:')
    print(f'  blueberry >= 6: {"PASSED" if berry_passed else "FAILED"} ({blueberry}/6)')
    print(f'  rawtuna >= 3: {"PASSED" if tuna_passed else "FAILED"} ({rawtuna}/3)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 20: Orchard Protection")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_20_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
