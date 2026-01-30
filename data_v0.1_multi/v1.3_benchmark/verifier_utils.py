"""
Utility functions for task verification in AgentWorld Multi-Agent Benchmark.
"""

import json
import re
from typing import Dict, List, Any, Tuple


def get_final_inventories(traj_json: Dict) -> Dict[str, List[Dict]]:
    """Extract final inventory for each agent from trajectory."""
    inventories = {}
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            agent_name = act.get('agent_name', '')
            obs = act.get('observation', {})
            if 'inventory' in obs and 'items' in obs['inventory']:
                inventories[agent_name] = obs['inventory']['items']
    return inventories


def aggregate_item_counts(inventories: Dict[str, List[Dict]]) -> Dict[str, int]:
    """Aggregate item counts across all agents into a single dict."""
    item_counts: Dict[str, int] = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x
    return item_counts


def get_all_inventories(traj_json: Dict) -> Dict[str, Dict[str, List[Dict]]]:
    """Extract all inventories for each agent across all rounds."""
    all_inventories = {}
    for r in traj_json.get('rounds', []):
        round_num = r.get('round', 0)
        for act in r.get('actions', []):
            agent_name = act.get('agent_name', '')
            obs = act.get('observation', {})
            if 'inventory' in obs and 'items' in obs['inventory']:
                if agent_name not in all_inventories:
                    all_inventories[agent_name] = {}
                all_inventories[agent_name][round_num] = obs['inventory']['items']
    return all_inventories


def count_item_in_inventories(inventories: Dict[str, List[Dict]], item_key: str) -> int:
    """Count total amount of an item across all inventories."""
    total = 0
    for items in inventories.values():
        for item in items:
            if item.get('key', '').lower() == item_key.lower():
                total += item.get('count', 0)
    return total


def has_item_in_any_inventory(inventories: Dict[str, List[Dict]], item_key: str, min_count: int = 1) -> bool:
    """Check if any agent has at least min_count of an item."""
    for items in inventories.values():
        for item in items:
            if item.get('key', '').lower() == item_key.lower():
                if item.get('count', 0) >= min_count:
                    return True
    return False


def check_agent_alive(traj_json: Dict, agent_name):
    # check if an agent is alive
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            agent_name = act.get('agent_name', '')
            if agent_name != agent_name:
                continue
            status = act.get('status', '')
            if '❤️' in status:
                hp_part = status.split('❤️')[1].split('|')[0].strip()
                current_hp = int(hp_part.split('/')[0])
                if current_hp <= 0:
                    return False
    return True


def check_agents_alive(traj_json: Dict) -> bool:
    """Check if all agents survived (HP > 0 in final state)."""
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            status = act.get('status', '')
            if '❤️' in status:
                hp_part = status.split('❤️')[1].split('|')[0].strip()
                current_hp = int(hp_part.split('/')[0])
                if current_hp <= 0:
                    return False
    return True


def get_final_hp(traj_json: Dict) -> Dict[str, int]:
    """Get final HP for each agent."""
    hp_map = {}
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            agent_name = act.get('agent_name', '')
            status = act.get('status', '')
            if '❤️' in status:
                hp_part = status.split('❤️')[1].split('|')[0].strip()
                current_hp = int(hp_part.split('/')[0])
                hp_map[agent_name] = current_hp
    return hp_map


def get_final_agent_status(traj_json: Dict) -> Dict[str, Dict]:
    """
    Get final HP status for all agents from the last round.
    Returns dict of {agent_name: {'current': hp, 'max': max_hp}}.
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
            current_hp = int(hp_match.group(1))
            max_hp = int(hp_match.group(2))
            agent_hp[agent_name] = {'current': current_hp, 'max': max_hp}
    return agent_hp


def get_final_agent_hp_simple(traj_json: Dict) -> Dict[str, int]:
    """Get final HP for all agents (simpler version returning just HP values)."""
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


def verify_combat(traj_json: Dict, target_name: str | None) -> int:
    if not target_name:
        # only count how many attacks are made
        attacks = 0
        for r in traj_json.get('rounds', []):
            for act in r.get('actions', []):
                action_str = act.get('action', '').lower()
                if 'attack_entity' in action_str:
                    attacks += 1
        return attacks
    # return number of kills of the target
    # Build a mapping from instance_id -> mob_name
    instance_to_name = {}
    print(instance_to_name)
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            mobs = act.get('observation', {}).get('mobs', [])
            for m in mobs:
                instance_id = m.get('instance', '')
                mob_name = m.get('name', '').lower()
                if instance_id and mob_name:
                    instance_to_name[instance_id] = mob_name
    
    print(f"Found {len(instance_to_name)} unique mob instances")
    
    # Track killed instances to avoid double counting
    killed_instances = set()
    kills = 0
    
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            if 'attack_entity' in action_str:
                # Check each known instance
                for instance_id, mob_name in instance_to_name.items():
                    # Check if this instance was attacked and matches target
                    if (instance_id in action_str and 
                        target_name.lower() in mob_name and 
                        instance_id not in killed_instances):
                        kills += 1
                        killed_instances.add(instance_id)
                        break
    return kills


def count_combat_kills(traj_json: Dict, target_patterns: List[str]) -> int:
    """Count kills of targets matching patterns by checking action results.

    NOTE: Attack actions use instance IDs (attack_entity(targetInstance=123456)),
    not mob names. So we check for mob names in observation/result strings,
    and also check chat messages for defeat confirmations.
    TODO: This check is not fully accurate - should look for 'VICTORY' in return value.
    """
    kills = 0
    killed_targets = set()  # Track killed targets to avoid double-counting

    kill_keywords = ['dead', 'killed', 'defeated', 'victory', 'died',
                     'slain', 'destroy', 'eliminated', 'vanquished', 'dropped',
                     'hp dropped to 0', 'hp: 0', 'health: 0']

    # HP zero patterns (covers different JSON formats)
    hp_zero_patterns = ['"hp": 0', '"hp":0', '"hitpoints": 0', '"hitpoints":0']

    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})
            result_str = str(act.get('result', '')).lower()

            # Build combined text to search for patterns and kill indicators
            combined_text = ''
            if isinstance(obs, dict):
                combined_text = json.dumps(obs).lower()
                # Also check mobs array directly for hitPoints: 0
                mobs = obs.get('mobs', [])
                for mob in mobs:
                    mob_name = mob.get('name', '').lower()
                    mob_hp = mob.get('hitPoints', -1)
                    if mob_hp == 0:
                        for pattern in target_patterns:
                            if pattern.lower() in mob_name:
                                if pattern.lower() not in killed_targets:
                                    kills += 1
                                    killed_targets.add(pattern.lower())
            elif isinstance(obs, str):
                combined_text = obs.lower()
            combined_text += ' ' + result_str

            # Check attack actions
            if 'attack' in action_str:
                # Check if any target pattern appears in observation/result
                for pattern in target_patterns:
                    pattern_lower = pattern.lower()
                    if pattern_lower in combined_text:
                        # Check for kill indicators
                        if any(kw in combined_text for kw in kill_keywords):
                            if pattern_lower not in killed_targets:
                                kills += 1
                                killed_targets.add(pattern_lower)
                        elif any(hp_pat in combined_text for hp_pat in hp_zero_patterns):
                            if pattern_lower not in killed_targets:
                                kills += 1
                                killed_targets.add(pattern_lower)

            # Also check chat messages for defeat confirmations
            if 'chat' in action_str or 'global_chat' in action_str:
                for pattern in target_patterns:
                    pattern_lower = pattern.lower()
                    if pattern_lower in combined_text:
                        if any(kw in combined_text for kw in kill_keywords):
                            if pattern_lower not in killed_targets:
                                kills += 1
                                killed_targets.add(pattern_lower)

    return kills


def check_boss_killed_by_loot(inventories: Dict[str, List[Dict]], loot_items: List[str]) -> bool:
    """Check if a boss was killed by verifying its loot drops are in inventory.

    This is useful when kill detection via combat messages is unreliable.
    For example, if wolfarmor is in inventory, Dark Wolf must have been killed.
    """
    for loot_item in loot_items:
        if has_item_in_any_inventory(inventories, loot_item):
            return True
    return False


def count_attack_actions(traj_json: Dict, target_patterns: List[str] = None) -> int:
    """Count successful attack actions, optionally filtering by target patterns."""
    attacks = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            if 'attack' in action_str:
                if target_patterns:
                    if any(p.lower() in action_str for p in target_patterns):
                        attacks += 1
                else:
                    attacks += 1
    return attacks


def count_crafted_items(traj_json: Dict) -> int:
    """Count items crafted during the task."""
    crafted = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})
            if 'craft' in action_str:
                if isinstance(obs, dict) and obs.get('status') == 'success':
                    crafted += 1
    return crafted


def check_crafted_items(traj_json: Dict, item_patterns: List[str]) -> Dict[str, int]:
    """Check if items matching patterns were crafted during the task."""
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


def count_chat_messages(traj_json: Dict) -> int:
    """Count chat/coordination messages."""
    chat_count = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            if 'chat' in action_str:
                chat_count += 1
    return chat_count


def get_agent_items_by_username(traj_json: Dict) -> Dict[str, Dict[str, int]]:
    """Get item counts for each agent, mapping by username from task definition."""
    task_def = traj_json.get('task_definition', {})
    agent_usernames = {}
    for key, value in task_def.items():
        if key.startswith('agent_') and isinstance(value, dict):
            agent_usernames[key] = value.get('username', key)

    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    agent_items = {}
    for agent_key, items in inventory.items():
        username = agent_usernames.get(agent_key, agent_key)
        item_counts = {}
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x
        agent_items[username] = item_counts

    return agent_items
