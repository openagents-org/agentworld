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


def count_combat_kills(traj_json: Dict, target_patterns: List[str]) -> int:
    """Count kills of targets matching patterns by checking action results."""
    kills = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})

            if 'attack' in action_str:
                for pattern in target_patterns:
                    if pattern.lower() in action_str:
                        if isinstance(obs, dict):
                            obs_str = json.dumps(obs).lower()
                            if 'dead' in obs_str or 'killed' in obs_str or 'defeated' in obs_str:
                                kills += 1
                            elif '"hp": 0' in obs_str or '"hp":0' in obs_str:
                                kills += 1
    return kills


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
