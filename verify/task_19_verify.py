"""
Task 19: Farm Defense Verification

Primary Objective: Successfully protect collectors while they gather 8x corn
and 4x tomato under agricultural threat conditions

Success:
- corn_harvester_agent has at least 8x corn in inventory
- tomato_gatherer_agent has at least 4x tomato in inventory
"""
import argparse
import json


def task_19_verifier(traj_json):
    """
    Verify Task 19: Farm Defense
    Check if corn_harvester_agent has 8+ corn and tomato_gatherer_agent has 4+ tomato
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

    # Check corn_harvester_agent for corn
    corn_harvester_items = {}
    for username, items in agent_items.items():
        if "corn_harvester" in username.lower():
            corn_harvester_items = items
            break

    # Check tomato_gatherer_agent for tomato
    tomato_gatherer_items = {}
    for username, items in agent_items.items():
        if "tomato_gatherer" in username.lower():
            tomato_gatherer_items = items
            break

    corn = corn_harvester_items.get("corn", 0)
    tomato = tomato_gatherer_items.get("tomato", 0)

    print(f'corn_harvester_agent corn: {corn}')
    print(f'tomato_gatherer_agent tomato: {tomato}')

    corn_passed = corn >= 8
    tomato_passed = tomato >= 4
    passed = corn_passed and tomato_passed

    print(f'\nChecks:')
    print(f'  corn >= 8: {"PASSED" if corn_passed else "FAILED"} ({corn}/8)')
    print(f'  tomato >= 4: {"PASSED" if tomato_passed else "FAILED"} ({tomato}/4)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 19: Farm Defense")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_19_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
