"""
Task 18: Coastal Harvest Verification

Primary Objective: Successfully protect collectors while they gather 6x rawshrimp
and 3x icelogs under coastal threat conditions

Success:
- shrimp_fisher_agent has at least 6x rawshrimp in inventory
- ice_logger_agent has at least 3x icelogs in inventory
"""
import argparse
import json


def task_18_verifier(traj_json):
    """
    Verify Task 18: Coastal Harvest
    Check if shrimp_fisher_agent has 6+ rawshrimp and ice_logger_agent has 3+ icelogs
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

    # Check shrimp_fisher_agent for rawshrimp
    shrimp_fisher_items = {}
    for username, items in agent_items.items():
        if "shrimp_fisher" in username.lower():
            shrimp_fisher_items = items
            break

    # Check ice_logger_agent for icelogs
    ice_logger_items = {}
    for username, items in agent_items.items():
        if "ice_logger" in username.lower():
            ice_logger_items = items
            break

    rawshrimp = shrimp_fisher_items.get("rawshrimp", 0)
    icelogs = ice_logger_items.get("icelogs", 0)

    print(f'shrimp_fisher_agent rawshrimp: {rawshrimp}')
    print(f'ice_logger_agent icelogs: {icelogs}')

    shrimp_passed = rawshrimp >= 6
    ice_passed = icelogs >= 3
    passed = shrimp_passed and ice_passed

    print(f'\nChecks:')
    print(f'  rawshrimp >= 6: {"PASSED" if shrimp_passed else "FAILED"} ({rawshrimp}/6)')
    print(f'  icelogs >= 3: {"PASSED" if ice_passed else "FAILED"} ({icelogs}/3)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 18: Coastal Harvest")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_18_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
