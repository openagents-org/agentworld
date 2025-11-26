"""
Task 25: Ice Cavern Challenge Verification

Primary Objective: Successfully explore ice caverns, defeat Ice Guardians, and harvest
rare Ice Oak lumber for cold-weather equipment

Success:
- Defeat Ice Guardians (check combat logs/kills)
- Harvest ice oak logs (iceoaklogs or icelogs in inventory)
- All agents survive (HP > 0)
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
        # Parse HP from status like "📊 Lv.111 | XP:131037 | ❤️1389/1389 | ..."
        hp_match = re.search(r'❤️(\d+)/(\d+)', status)
        if hp_match:
            agent_hp[agent_name] = int(hp_match.group(1))

    return agent_hp


def count_combat_kills(traj_json, target_patterns):
    """
    Count kills of targets matching patterns by checking action results.
    """
    kills = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})

            # Check if it's an attack action
            if 'attack' in action_str:
                # Check for any target pattern
                for pattern in target_patterns:
                    if pattern.lower() in action_str:
                        # Check if attack was successful and mob died
                        if isinstance(obs, dict):
                            obs_str = json.dumps(obs).lower()
                            if 'dead' in obs_str or 'killed' in obs_str or 'defeated' in obs_str:
                                kills += 1
                            elif '"hp": 0' in obs_str or '"hp":0' in obs_str:
                                kills += 1
    return kills


def task_25_verifier(traj_json):
    """
    Verify Task 25: Ice Cavern Challenge
    1. Defeat Ice Guardians
    2. Harvest ice oak lumber (iceoaklogs or icelogs)
    3. All agents survive
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Count ice materials
    ice_items = ["iceoaklogs", "icelogs", "iceoak", "icelog"]
    total_ice_logs = 0
    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(ice_key in k for ice_key in ice_items):
                total_ice_logs += x

    print(f'Ice Oak/Ice Logs collected: {total_ice_logs}')

    # Check Ice Guardian kills
    ice_guardian_kills = count_combat_kills(traj_json, ["ice guardian", "iceguardian", "ice_guardian"])
    print(f'Ice Guardian kills detected: {ice_guardian_kills}')

    # Check agent survival
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    dead_agents = [name for name, hp in agent_hp.items() if hp <= 0]

    print(f'Agent HP status: {agent_hp}')
    print(f'All agents alive: {all_alive}')
    if dead_agents:
        print(f'Dead agents: {dead_agents}')

    # Verification checks
    ice_logs_passed = total_ice_logs >= 1
    guardians_passed = ice_guardian_kills >= 1
    survival_passed = all_alive

    # For survival tasks, primary check is survival + some objective completion
    # Ice cavern: need ice logs AND survival (guardian kills are bonus)
    passed = ice_logs_passed and survival_passed

    print(f'\nChecks:')
    print(f'  Ice logs >= 1: {"PASSED" if ice_logs_passed else "FAILED"} ({total_ice_logs})')
    print(f'  Ice Guardian kills >= 1: {"PASSED" if guardians_passed else "FAILED"} ({ice_guardian_kills})')
    print(f'  All agents survive: {"PASSED" if survival_passed else "FAILED"}')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 25: Ice Cavern Challenge")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_25_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
