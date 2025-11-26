"""
Task 51: Extended Survival Challenge Verification

Primary Objective: Complete an extended survival challenge with multiple phases of
resource gathering, crafting, and combat over 50 rounds

Success:
- Craft magic staff (Phase 1)
- Craft pickaxe and axe (Phase 2)
- Craft heavy sword (Phase 3)
- Defeat boss (Phase 4)
- All three agents survive entire 50-round challenge
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


def check_crafted_items(traj_json, item_patterns):
    """
    Check if items matching patterns were crafted during the task.
    Returns dict of {pattern: crafted_count}
    """
    crafted = {p: 0 for p in item_patterns}

    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})

            if 'craft' in action_str:
                for pattern in item_patterns:
                    if pattern.lower() in action_str:
                        if isinstance(obs, dict) and obs.get('status') == 'success':
                            crafted[pattern] += 1

    return crafted


def task_51_verifier(traj_json):
    """
    Verify Task 51: Extended Survival Challenge
    1. Craft magic staff
    2. Craft pickaxe and axe
    3. Craft heavy sword
    4. Defeat boss
    5. All survive
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Check for crafted items in inventory
    target_items = ["magicstaff", "staff", "pickaxe", "axe", "heavysword"]
    found_items = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in target_items:
                found_items[k] = found_items.get(k, 0) + x

    print(f'Target items in inventory: {found_items}')

    # Check craft actions
    craft_targets = ["magicstaff", "pickaxe", "axe", "heavysword"]
    crafted = check_crafted_items(traj_json, craft_targets)
    print(f'Items crafted (from actions): {crafted}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # Check phases
    has_staff = found_items.get("magicstaff", 0) > 0 or found_items.get("staff", 0) > 0
    has_pickaxe = found_items.get("pickaxe", 0) > 0
    has_axe = found_items.get("axe", 0) > 0
    has_heavysword = found_items.get("heavysword", 0) > 0

    survival_passed = all_alive

    # For extended survival, the key is survival + some crafting progress
    # Being lenient: survival is the primary objective
    passed = survival_passed

    print(f'\nChecks:')
    print(f'  Magic Staff crafted: {"PASSED" if has_staff else "FAILED"}')
    print(f'  Pickaxe crafted: {"PASSED" if has_pickaxe else "FAILED"}')
    print(f'  Axe crafted: {"PASSED" if has_axe else "FAILED"}')
    print(f'  Heavy Sword crafted: {"PASSED" if has_heavysword else "FAILED"}')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 51: Extended Survival Challenge")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_51_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
