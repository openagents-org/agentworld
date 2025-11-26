"""
Task 67: Multi-Biome Resource Caravan Verification

Primary Objective: Establish continental trading route visiting 6 biomes,
gather 80+ unique resources, craft 12+ regional specialty items

Success:
- Gather 80+ total resources
- Craft 12+ regional specialty items
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


def task_67_verifier(traj_json):
    """
    Verify Task 67: Multi-Biome Resource Caravan
    - 80+ total resources gathered
    - 12+ items crafted
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Define resource types (raw materials)
    resource_keys = [
        "logs", "oak", "palm", "ice", "stick", "coal", "ironore", "goldore",
        "rawshrimp", "rawtuna", "jellyfish", "crab", "fish", "herb", "apple",
        "peach", "blueberry", "corn", "tomato", "cactus", "feather", "string", "bead"
    ]

    # Define crafted items
    crafted_keys = [
        "ironbar", "goldbar", "sword", "axe", "pickaxe", "bow", "arrow",
        "cookedshrimp", "cookedtuna", "ring", "staff", "armor", "boots"
    ]

    # Count resources and crafted items
    total_resources = 0
    total_crafted = 0
    resource_breakdown = {}
    crafted_breakdown = {}
    starting_items = ["flask", "apple"]

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)

            # Skip starting items for resource count
            if k in starting_items:
                continue

            # Check if it's a resource
            is_resource = any(res in k for res in resource_keys)
            # Check if it's a crafted item
            is_crafted = any(craft in k for craft in crafted_keys)

            if is_resource:
                total_resources += x
                resource_breakdown[k] = resource_breakdown.get(k, 0) + x
            elif is_crafted:
                total_crafted += x
                crafted_breakdown[k] = crafted_breakdown.get(k, 0) + x

    print(f'Total resources gathered: {total_resources}')
    print(f'Resource breakdown: {resource_breakdown}')
    print(f'\nTotal items crafted: {total_crafted}')
    print(f'Crafted breakdown: {crafted_breakdown}')

    # Check survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    print(f'\nAll agents alive: {all_alive}')

    # Verification
    resources_passed = total_resources >= 80
    crafted_passed = total_crafted >= 12

    passed = resources_passed and crafted_passed

    print(f'\nChecks:')
    print(f'  Resources >= 80: {"PASSED" if resources_passed else "FAILED"} ({total_resources}/80)')
    print(f'  Crafted items >= 12: {"PASSED" if crafted_passed else "FAILED"} ({total_crafted}/12)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 67: Multi-Biome Resource Caravan")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_67_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
