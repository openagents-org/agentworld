"""
Task 17: Forest Gathering Verification

Primary Objective: Successfully protect collectors while they gather 4x palmlogs
and 5x peach under wildlife threat conditions

Success:
- palm_logger_agent has at least 4x palmlogs in inventory
- peach_forager_agent has at least 5x peach in inventory
"""
import argparse
import json


def task_17_verifier(traj_json):
    """
    Verify Task 17: Forest Gathering
    Check if palm_logger_agent has 4+ palmlogs and peach_forager_agent has 5+ peach
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

    # Check palm_logger_agent for palmlogs
    palm_logger_items = {}
    for username, items in agent_items.items():
        if "palm_logger" in username.lower():
            palm_logger_items = items
            break

    # Check peach_forager_agent for peach
    peach_forager_items = {}
    for username, items in agent_items.items():
        if "peach_forager" in username.lower():
            peach_forager_items = items
            break

    palmlogs = palm_logger_items.get("palmlogs", 0)
    peach = peach_forager_items.get("peach", 0)

    print(f'palm_logger_agent palmlogs: {palmlogs}')
    print(f'peach_forager_agent peach: {peach}')

    palm_passed = palmlogs >= 4
    peach_passed = peach >= 5
    passed = palm_passed and peach_passed

    print(f'\nChecks:')
    print(f'  palmlogs >= 4: {"PASSED" if palm_passed else "FAILED"} ({palmlogs}/4)')
    print(f'  peach >= 5: {"PASSED" if peach_passed else "FAILED"} ({peach}/5)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 17: Forest Gathering")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_17_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
