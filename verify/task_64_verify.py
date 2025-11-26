"""
Task 64: Ice Region Survival Expedition Verification

Primary Objective: Complete ice expedition: gather 50+ ice materials, hunt 15+ ice
creatures, craft 8+ cold-weather items

Success:
- Gather 50+ ice materials (ice logs, ice palm logs, coal, etc.)
- Hunt 15+ ice creatures
- Craft 8+ cold-weather items
- All agents survive (HP > 0)
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


def count_attack_actions(traj_json, target_patterns=None):
    """
    Count successful attack actions, optionally filtering by target patterns.
    """
    attacks = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})

            if 'attack' in action_str:
                if target_patterns:
                    if any(p.lower() in action_str for p in target_patterns):
                        attacks += 1
                else:
                    attacks += 1
    return attacks


def count_crafted_items(traj_json):
    """
    Count items crafted during the task.
    """
    crafted = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})

            if 'craft' in action_str:
                if isinstance(obs, dict) and obs.get('status') == 'success':
                    crafted += 1
    return crafted


def task_64_verifier(traj_json):
    """
    Verify Task 64: Ice Region Survival Expedition
    1. Gather 50+ ice materials
    2. Hunt 15+ ice creatures
    3. Craft 8+ items
    4. All agents survive
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count ice materials
    ice_items = ["icelogs", "icelog", "icepalm", "iceoaklogs", "coal", "ice"]
    total_ice_materials = 0
    ice_breakdown = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(ice_key in k for ice_key in ice_items):
                total_ice_materials += x
                ice_breakdown[k] = ice_breakdown.get(k, 0) + x

    print(f'Ice materials collected: {total_ice_materials}')
    if ice_breakdown:
        print(f'Ice breakdown: {ice_breakdown}')

    # Count ice creature kills
    ice_creatures = ["icerat", "icebat", "icecrab", "icegoblin", "ice"]
    ice_kills = count_attack_actions(traj_json, ice_creatures)
    print(f'Ice creature attacks: {ice_kills}')

    # Count crafted items
    crafted_items = count_crafted_items(traj_json)
    print(f'Items crafted: {crafted_items}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # Verification
    ice_materials_passed = total_ice_materials >= 50
    ice_kills_passed = ice_kills >= 15
    crafted_passed = crafted_items >= 8
    survival_passed = all_alive

    # Primary objective requires all conditions
    passed = ice_materials_passed and ice_kills_passed and crafted_passed and survival_passed

    print(f'\nChecks:')
    print(f'  Ice materials >= 50: {"PASSED" if ice_materials_passed else "FAILED"} ({total_ice_materials}/50)')
    print(f'  Ice creature kills >= 15: {"PASSED" if ice_kills_passed else "FAILED"} ({ice_kills}/15)')
    print(f'  Items crafted >= 8: {"PASSED" if crafted_passed else "FAILED"} ({crafted_items}/8)')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 64: Ice Region Survival Expedition")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_64_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
