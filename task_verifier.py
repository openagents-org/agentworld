"""
Task Verifier for AgentWorld Multi-Agent Benchmark
Covers: Combat, Construction, Crafting, and Exploration tasks

Usage:
    python task_verifier.py --traj_path path/to/task_XX_trajectory.json
    
The task ID is automatically parsed from the filename (e.g., task_10_trajectory.json -> task_10)
"""

import argparse
import json
import re
import os
from typing import Dict, List, Any, Tuple


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

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
    Returns dict of {agent_name: {'current': hp, 'max': max_hp}} or just int for simpler verifiers.
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


def parse_task_id_from_path(traj_path: str) -> str:
    """Parse task ID from trajectory filename (e.g., task_10_trajectory.json -> task_10)."""
    basename = os.path.basename(traj_path)
    # Match patterns like task_XX_trajectory.json or task_XX.json
    match = re.search(r'task_(\d+)', basename)
    if match:
        return f"task_{match.group(1)}"
    return None


# =============================================================================
# COMBAT TASKS (16, 28, 29, 30, 35, 36, 50, 55, 72, 77, 88, 91)
# =============================================================================

def task_16_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Resource Protection Mission - protect collectors while gathering resources."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_agents_alive(traj_json)
    
    success = logs >= 5 and blueberry >= 3 and alive
    msg = f"Logs: {logs}/5, Blueberry: {blueberry}/3, All alive: {alive}"
    return (1 if success else 0, msg)


def task_28_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Dark Forest Cleansing - defeat Dark Wolf boss."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_29_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Castle Siege Warfare - defeat Ice Knight."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_30_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ultimate Boss Challenge - defeat multiple legendary bosses."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_35_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Strategic Combat Training - combat training exercises."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_36_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Combat Operations - hunt challenging creatures."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_50_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Combat Battalion - defeat 4 tiers of enemies."""
    alive = check_agents_alive(traj_json)
    hp_map = get_final_hp(traj_json)
    survivors = sum(1 for hp in hp_map.values() if hp > 0)
    total = len(hp_map)
    
    success = survivors >= 4  # At least 4 out of 5 survive
    msg = f"Survivors: {survivors}/{total}, All alive: {alive}"
    return (1 if success else 0, msg)


def task_55_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Epic Boss Raid Campaign - 7-phase boss raid."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_72_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress Siege Defense - defend against 4 waves."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_77_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Harbor Bastion - coastal defense."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    
    success = alive and cookedshrimp >= 20
    msg = f"All alive: {alive}, Cooked shrimp: {cookedshrimp}/20"
    return (1 if success else 0, msg)


def task_88_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stormfront War Council - defeat 3 guardian bosses."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_91_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Royal Tournament - 3 challenges."""
    inventories = get_final_inventories(traj_json)
    
    legendary_items = ['heavysword', 'goldring', 'icestaff', 'silverring', 'axe', 'emeraldpendant']
    legendary_count = sum(1 for item in legendary_items if has_item_in_any_inventory(inventories, item))
    
    food_items = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, item) for item in food_items)
    
    alive = check_agents_alive(traj_json)
    success = alive and legendary_count >= 5 and food_count >= 20
    msg = f"Alive: {alive}, Legendary items: {legendary_count}/5, Food: {food_count}/20"
    return (1 if success else 0, msg)


# =============================================================================
# CONSTRUCTION TASKS (41, 43, 74, 76, 81, 84, 87, 89, 90, 93)
# =============================================================================

def task_41_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Construction Engineering - infrastructure development."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_43_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Environmental Protection."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_74_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Guild Headquarters Establishment."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    logs = count_item_in_inventories(inventories, 'logs')
    
    msg = f"Alive: {alive}, Iron bars: {ironbar}, Logs: {logs}"
    return (1 if alive else 0, msg)


def task_76_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Nexus Stabilization - stabilize 3 shrines."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    
    staffs = ['firestaff', 'lightningstaff', 'naturestaff', 'icestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))
    
    success = alive and staff_count >= 3
    msg = f"Alive: {alive}, Elemental staffs: {staff_count}/3"
    return (1 if success else 0, msg)


def task_81_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Cryothermal Grid."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_84_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Underground Railway Restoration."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_87_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mirefall Canal Restoration."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_89_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Astral Beacon Calibration."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_90_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stormspire Barrier Reboot."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_93_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress Defense Construction."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


# =============================================================================
# CRAFTING TASKS
# =============================================================================

def task_00_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Cooperative Workshop - 3 projects: staff, 10 arrows, silver ring."""
    inventories = get_final_inventories(traj_json)
    
    staff = has_item_in_any_inventory(inventories, 'staff')
    arrows = count_item_in_inventories(inventories, 'arrow')
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    
    success = staff and arrows >= 10 and silverring
    msg = f"Staff: {staff}, Arrows: {arrows}/10, Silver ring: {silverring}"
    return (1 if success else 0, msg)


def task_01_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magic Staff Crafting."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    msg = f"Staff crafted: {staff}"
    return (1 if staff else 0, msg)


def task_02_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Arrow Production - produce 10 arrows."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    success = arrows >= 10
    msg = f"Arrows: {arrows}/10"
    return (1 if success else 0, msg)


def task_03_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Silver Ring Forging."""
    inventories = get_final_inventories(traj_json)
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    msg = f"Silver ring: {silverring}"
    return (1 if silverring else 0, msg)


def task_05_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Beryl Pendant Crafting."""
    inventories = get_final_inventories(traj_json)
    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    msg = f"Beryl pendant: {berylpendant}"
    return (1 if berylpendant else 0, msg)


def task_06_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Heavy Sword Forging."""
    inventories = get_final_inventories(traj_json)
    heavysword = has_item_in_any_inventory(inventories, 'sword2') or has_item_in_any_inventory(inventories, 'heavysword')
    msg = f"Heavy sword: {heavysword}"
    return (1 if heavysword else 0, msg)


def task_07_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Pickaxe Crafting."""
    inventories = get_final_inventories(traj_json)
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')
    msg = f"Pickaxe count: {pickaxe}"
    return (1 if pickaxe >= 1 else 0, msg)


def task_08_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Bronze Alloy Creation."""
    inventories = get_final_inventories(traj_json)
    bronzebar = has_item_in_any_inventory(inventories, 'bronzebar')
    msg = f"Bronze bar: {bronzebar}"
    return (1 if bronzebar else 0, msg)


def task_09_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Topaz Ring Crafting."""
    inventories = get_final_inventories(traj_json)
    topazring = has_item_in_any_inventory(inventories, 'topazring')
    msg = f"Topaz ring: {topazring}"
    return (1 if topazring else 0, msg)


def task_10_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stew Cooking."""
    inventories = get_final_inventories(traj_json)
    stew = has_item_in_any_inventory(inventories, 'stew2') or has_item_in_any_inventory(inventories, 'stew')
    msg = f"Stew: {stew}"
    return (1 if stew else 0, msg)


def task_11_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Lightning Staff Enhancement."""
    inventories = get_final_inventories(traj_json)
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    msg = f"Lightning staff: {lightningstaff}"
    return (1 if lightningstaff else 0, msg)


def task_12_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gold Ring Forging."""
    inventories = get_final_inventories(traj_json)
    goldring = has_item_in_any_inventory(inventories, 'goldring')
    msg = f"Gold ring: {goldring}"
    return (1 if goldring else 0, msg)


def task_13_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Bucket Crafting."""
    inventories = get_final_inventories(traj_json)
    bucket = has_item_in_any_inventory(inventories, 'bucket')
    msg = f"Bucket: {bucket}"
    return (1 if bucket else 0, msg)


def task_14_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Shrimp Cooking."""
    inventories = get_final_inventories(traj_json)
    cookedshrimp = has_item_in_any_inventory(inventories, 'cookedshrimp')
    msg = f"Cooked shrimp: {cookedshrimp}"
    return (1 if cookedshrimp else 0, msg)


def task_15_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Jellyfish Smoothie - create a jellyfish smoothie."""
    inventories = get_final_inventories(traj_json)
    jellyfishsmoothie = count_item_in_inventories(inventories, 'jellyfishsmoothie')
    
    passed = jellyfishsmoothie >= 1
    msg = f"Jellyfish smoothie: {jellyfishsmoothie}/1"
    return (1 if passed else 0, msg)


def task_22_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magical Defense - craft lightning staff and defeat Ice Wizard."""
    inventories = get_final_inventories(traj_json)
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    alive = check_agents_alive(traj_json)
    
    success = lightningstaff and alive
    msg = f"Lightning staff: {lightningstaff}, All alive: {alive}"
    return (1 if success else 0, msg)


def task_27_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Volcanic Forge."""
    inventories = get_final_inventories(traj_json)
    alive = check_agents_alive(traj_json)
    msg = f"All alive: {alive}"
    return (1 if alive else 0, msg)


def task_31_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Woodworking Coordination."""
    inventories = get_final_inventories(traj_json)
    stick = count_item_in_inventories(inventories, 'stick')
    logs = count_item_in_inventories(inventories, 'logs')
    msg = f"Sticks: {stick}, Logs: {logs}"
    return (1 if stick >= 10 or logs >= 5 else 0, msg)


def task_34_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magical Workshop."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    msg = f"Staff: {staff}"
    return (1 if staff else 0, msg)


def task_39_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Agricultural Development."""
    inventories = get_final_inventories(traj_json)
    alive = check_agents_alive(traj_json)
    msg = f"All alive: {alive}"
    return (1 if alive else 0, msg)


def task_47_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magical Research Institute."""
    inventories = get_final_inventories(traj_json)
    staffs = ['staff', 'lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    has_staff = any(has_item_in_any_inventory(inventories, s) for s in staffs)
    msg = f"Has magical staff: {has_staff}"
    return (1 if has_staff else 0, msg)


def task_49_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Jewelry Workshop."""
    inventories = get_final_inventories(traj_json)
    jewelry = ['silverring', 'goldring', 'topazring', 'berylpendant', 'emeraldpendant']
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))
    success = jewelry_count >= 3
    msg = f"Jewelry items: {jewelry_count}/3"
    return (1 if success else 0, msg)


def task_52_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Comprehensive Smithy."""
    inventories = get_final_inventories(traj_json)
    weapons = ['sword2', 'heavysword', 'axe', 'pickaxe']
    weapon_count = sum(1 for w in weapons if has_item_in_any_inventory(inventories, w))
    msg = f"Weapons crafted: {weapon_count}"
    return (1 if weapon_count >= 2 else 0, msg)


def task_54_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Archery Academy."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    bow = has_item_in_any_inventory(inventories, 'woodenbow') or has_item_in_any_inventory(inventories, 'bow')
    success = arrows >= 30 and bow
    msg = f"Arrows: {arrows}/30, Has bow: {bow}"
    return (1 if success else 0, msg)


def task_58_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Harvest Festival."""
    inventories = get_final_inventories(traj_json)
    food_items = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food_items)
    success = food_count >= 20
    msg = f"Food items: {food_count}/20"
    return (1 if success else 0, msg)


def task_61_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Royal Banquet Preparation."""
    inventories = get_final_inventories(traj_json)
    food_items = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food_items)
    success = food_count >= 15
    msg = f"Food items: {food_count}/15"
    return (1 if success else 0, msg)


def task_62_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Weaponsmith Consortium."""
    inventories = get_final_inventories(traj_json)
    weapons = ['sword2', 'heavysword', 'bluesword', 'axe']
    weapon_count = sum(count_item_in_inventories(inventories, w) for w in weapons)
    success = weapon_count >= 3
    msg = f"Weapons: {weapon_count}/3"
    return (1 if success else 0, msg)


def task_63_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Enchanted Jewelry Workshop."""
    inventories = get_final_inventories(traj_json)
    jewelry = ['silverring', 'goldring', 'topazring', 'berylpendant']
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))
    success = jewelry_count >= 2
    msg = f"Jewelry: {jewelry_count}/2"
    return (1 if success else 0, msg)


def task_65_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Alchemist Guild Potions."""
    inventories = get_final_inventories(traj_json)
    potions = ['healthpotion', 'manapotion', 'jellyfishsmoothie']
    potion_count = sum(count_item_in_inventories(inventories, p) for p in potions)
    msg = f"Potions/consumables: {potion_count}"
    return (1 if potion_count >= 5 else 0, msg)


def task_66_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Archery Competition."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    success = arrows >= 20
    msg = f"Arrows: {arrows}/20"
    return (1 if success else 0, msg)


def task_68_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Master Toolsmith Consortium."""
    inventories = get_final_inventories(traj_json)
    tools = ['pickaxe', 'axe', 'fishingpole', 'fishingrod']
    tool_count = sum(count_item_in_inventories(inventories, t) for t in tools)
    success = tool_count >= 3
    msg = f"Tools: {tool_count}/3"
    return (1 if success else 0, msg)


def task_69_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Legendary Equipment Forge."""
    inventories = get_final_inventories(traj_json)
    legendary = ['goldensword', 'goldenbow', 'goldring', 'lightningstaff', 'firestaff']
    legendary_count = sum(1 for l in legendary if has_item_in_any_inventory(inventories, l))
    success = legendary_count >= 2
    msg = f"Legendary items: {legendary_count}/2"
    return (1 if success else 0, msg)


def task_86_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Tri-Forge Vanguard."""
    inventories = get_final_inventories(traj_json)
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')
    
    success = heavysword >= 4 and goldenbow >= 3 and lightningstaff >= 2 and firestaff >= 2
    msg = f"Heavy swords: {heavysword}/4, Golden bows: {goldenbow}/3, Lightning staffs: {lightningstaff}/2, Fire staffs: {firestaff}/2"
    return (1 if success else 0, msg)


def task_97_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Agricultural Empire."""
    inventories = get_final_inventories(traj_json)
    crops = ['corn', 'tomato', 'blueberry', 'apple']
    crop_count = sum(count_item_in_inventories(inventories, c) for c in crops)
    success = crop_count >= 30
    msg = f"Crops: {crop_count}/30"
    return (1 if success else 0, msg)


# =============================================================================
# EXPLORATION TASKS (100, 21, 23, 24, 33, 46, 48, 53, 57, 60, 70, 73, 79, 95)
# =============================================================================

def task_21_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deep Mining Expedition - mine gold and craft golden ring."""
    inventories = get_final_inventories(traj_json)
    goldring = has_item_in_any_inventory(inventories, 'goldring')
    msg = f"Gold ring: {goldring}"
    return (1 if goldring else 0, msg)


def task_23_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Underwater Expedition - recover Trident."""
    inventories = get_final_inventories(traj_json)
    trident = has_item_in_any_inventory(inventories, 'trident')
    alive = check_agents_alive(traj_json)
    success = trident and alive
    msg = f"Trident: {trident}, All alive: {alive}"
    return (1 if success else 0, msg)


def task_24_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ancient Ruins Exploration - defeat guardians."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_33_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Resource Expedition."""
    inventories = get_final_inventories(traj_json)
    resources = ['logs', 'ironore', 'coal', 'goldore']
    resource_count = sum(count_item_in_inventories(inventories, r) for r in resources)
    success = resource_count >= 20
    msg = f"Resources: {resource_count}/20"
    return (1 if success else 0, msg)


def task_46_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Mining Expedition."""
    inventories = get_final_inventories(traj_json)
    ores = ['ironore', 'goldore', 'coal', 'copperore', 'tinore']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)
    success = ore_count >= 30
    msg = f"Ores: {ore_count}/30"
    return (1 if success else 0, msg)


def task_48_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Epic Cross-Region Expedition."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_53_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Advanced Culinary Expedition."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    success = food_count >= 10
    msg = f"Cooked food: {food_count}/10"
    return (1 if success else 0, msg)


def task_57_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Jewelry Expedition."""
    inventories = get_final_inventories(traj_json)
    gems = ['beryl', 'topaz', 'emerald', 'ruby', 'sapphire']
    gem_count = sum(count_item_in_inventories(inventories, g) for g in gems)
    jewelry = ['silverring', 'goldring', 'topazring', 'berylpendant']
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))
    success = gem_count >= 5 or jewelry_count >= 2
    msg = f"Gems: {gem_count}, Jewelry: {jewelry_count}"
    return (1 if success else 0, msg)


def task_60_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Underground Mining Expedition."""
    inventories = get_final_inventories(traj_json)
    ores = ['ironore', 'goldore', 'coal']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)
    bars = ['ironbar', 'goldbar']
    bar_count = sum(count_item_in_inventories(inventories, b) for b in bars)
    success = ore_count >= 15 or bar_count >= 5
    msg = f"Ores: {ore_count}, Bars: {bar_count}"
    return (1 if success else 0, msg)


def task_70_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Progressive Dungeon Expedition."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_73_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Mastery Expedition."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))
    success = alive and staff_count >= 2
    msg = f"All alive: {alive}, Elemental staffs: {staff_count}/2"
    return (1 if success else 0, msg)


def task_79_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Dragon Hunt Expedition."""
    alive = check_agents_alive(traj_json)
    hp_map = get_final_hp(traj_json)
    survivors = sum(1 for hp in hp_map.values() if hp > 0)
    total = len(hp_map)
    success = survivors >= 8  # At least 8/10 survive
    msg = f"Survivors: {survivors}/{total}"
    return (1 if success else 0, msg)


def task_95_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deep Ocean Expedition."""
    inventories = get_final_inventories(traj_json)
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    jellyfish = count_item_in_inventories(inventories, 'jellyfish')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    
    seafood = rawshrimp + jellyfish
    cooked = cookedshrimp
    success = seafood >= 50 and cooked >= 40
    msg = f"Raw seafood: {seafood}/50, Cooked shrimp: {cooked}/40"
    return (1 if success else 0, msg)


def task_100_verifier(traj_json: Dict) -> Tuple[int, str]:
    """World Resource Survey."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    
    resource_types = ['logs', 'ironore', 'coal', 'goldore', 'blueberry', 'corn', 'rawshrimp']
    found_types = sum(1 for r in resource_types if count_item_in_inventories(inventories, r) > 0)
    
    success = alive and found_types >= 5
    msg = f"All alive: {alive}, Resource types found: {found_types}/5"
    return (1 if success else 0, msg)


# =============================================================================
# SPECIALIZED TASKS FROM verify/ FOLDER
# =============================================================================

def task_17_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forest Gathering - palm_logger needs 4+ palmlogs, peach_forager needs 5+ peach."""
    agent_items = get_agent_items_by_username(traj_json)
    
    palm_logger_items = {}
    for username, items in agent_items.items():
        if "palm_logger" in username.lower():
            palm_logger_items = items
            break

    peach_forager_items = {}
    for username, items in agent_items.items():
        if "peach_forager" in username.lower():
            peach_forager_items = items
            break

    palmlogs = palm_logger_items.get("palmlogs", 0)
    peach = peach_forager_items.get("peach", 0)

    palm_passed = palmlogs >= 4
    peach_passed = peach >= 5
    passed = palm_passed and peach_passed

    msg = f"palmlogs: {palmlogs}/4, peach: {peach}/5"
    return (1 if passed else 0, msg)


def task_18_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Coastal Harvest - shrimp_fisher needs 6+ rawshrimp, ice_logger needs 3+ icelogs."""
    agent_items = get_agent_items_by_username(traj_json)

    shrimp_fisher_items = {}
    for username, items in agent_items.items():
        if "shrimp_fisher" in username.lower():
            shrimp_fisher_items = items
            break

    ice_logger_items = {}
    for username, items in agent_items.items():
        if "ice_logger" in username.lower():
            ice_logger_items = items
            break

    rawshrimp = shrimp_fisher_items.get("rawshrimp", 0)
    icelogs = ice_logger_items.get("icelogs", 0)

    shrimp_passed = rawshrimp >= 6
    ice_passed = icelogs >= 3
    passed = shrimp_passed and ice_passed

    msg = f"rawshrimp: {rawshrimp}/6, icelogs: {icelogs}/3"
    return (1 if passed else 0, msg)


def task_19_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Farm Defense - corn_harvester needs 8+ corn, tomato_gatherer needs 4+ tomato."""
    agent_items = get_agent_items_by_username(traj_json)

    corn_harvester_items = {}
    for username, items in agent_items.items():
        if "corn_harvester" in username.lower():
            corn_harvester_items = items
            break

    tomato_gatherer_items = {}
    for username, items in agent_items.items():
        if "tomato_gatherer" in username.lower():
            tomato_gatherer_items = items
            break

    corn = corn_harvester_items.get("corn", 0)
    tomato = tomato_gatherer_items.get("tomato", 0)

    corn_passed = corn >= 8
    tomato_passed = tomato >= 4
    passed = corn_passed and tomato_passed

    msg = f"corn: {corn}/8, tomato: {tomato}/4"
    return (1 if passed else 0, msg)


def task_20_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Orchard Protection - berry_picker needs 6+ blueberry, pond_fisher needs 3+ rawtuna."""
    agent_items = get_agent_items_by_username(traj_json)

    berry_picker_items = {}
    for username, items in agent_items.items():
        if "berry_picker" in username.lower():
            berry_picker_items = items
            break

    pond_fisher_items = {}
    for username, items in agent_items.items():
        if "pond_fisher" in username.lower():
            pond_fisher_items = items
            break

    blueberry = berry_picker_items.get("blueberry", 0)
    rawtuna = pond_fisher_items.get("rawtuna", 0)

    berry_passed = blueberry >= 6
    tuna_passed = rawtuna >= 3
    passed = berry_passed and tuna_passed

    msg = f"blueberry: {blueberry}/6, rawtuna: {rawtuna}/3"
    return (1 if passed else 0, msg)


def task_25_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ice Cavern Challenge - harvest ice logs and survive."""
    inventories = get_final_inventories(traj_json)
    
    ice_items = ["iceoaklogs", "icelogs", "iceoak", "icelog"]
    total_ice_logs = 0
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(ice_key in k for ice_key in ice_items):
                total_ice_logs += x

    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    ice_logs_passed = total_ice_logs >= 1
    survival_passed = all_alive
    passed = ice_logs_passed and survival_passed

    msg = f"Ice logs: {total_ice_logs}/1, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def task_26_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Desert Caravan Trading - all agents survive."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_32_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Wilderness Expedition - all agents survive."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_37_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Survival Expedition - all agents survive."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_38_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Trade Network Operations - all agents survive within 34 rounds."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 34

    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/34"
    return (1 if passed else 0, msg)


def task_40_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Medical Emergency Response - all agents survive."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_42_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Educational Training - all agents survive within 40 rounds."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 40

    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/40"
    return (1 if passed else 0, msg)


def task_44_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Communication Network - all agents survive within 43 rounds."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 43

    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/43"
    return (1 if passed else 0, msg)


def task_45_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Transportation Logistics - all agents survive within 45 rounds."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 45

    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/45"
    return (1 if passed else 0, msg)


def task_51_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Extended Survival Challenge - all agents survive."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_56_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Cross-Region Trading Network - 3x goldring, 2x lightningstaff, 1x heavysword."""
    inventories = get_final_inventories(traj_json)
    
    goldring = count_item_in_inventories(inventories, 'goldring')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')

    goldring_passed = goldring >= 3
    staff_passed = lightningstaff >= 2
    sword_passed = heavysword >= 1

    passed = goldring_passed and staff_passed and sword_passed
    msg = f"Gold Rings: {goldring}/3, Lightning Staffs: {lightningstaff}/2, Heavy Swords: {heavysword}/1"
    return (1 if passed else 0, msg)


def task_59_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Merchant Guild - 4x golden items, 3x staffs, 2x specialty weapons."""
    inventories = get_final_inventories(traj_json)
    
    golden_items = ["goldensword", "goldenbow", "goldenboots", "goldring", "goldenring"]
    elemental_staffs = ["lightningstaff", "firestaff", "icestaff"]
    specialty_weapons = ["pickaxe", "heavysword", "sword2"]

    golden_count = 0
    staff_count = 0
    weapon_count = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)

            if k in golden_items:
                golden_count += x
            elif k in elemental_staffs:
                staff_count += x
            elif k in specialty_weapons:
                weapon_count += x

    golden_passed = golden_count >= 4
    staff_passed = staff_count >= 3
    weapon_passed = weapon_count >= 2

    passed = golden_passed and staff_passed and weapon_passed
    msg = f"Golden items: {golden_count}/4, Staffs: {staff_count}/3, Weapons: {weapon_count}/2"
    return (1 if passed else 0, msg)


def task_64_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ice Region Survival Expedition - 50+ ice materials, 15+ kills, 8+ crafts, all survive."""
    inventories = get_final_inventories(traj_json)
    
    ice_items = ["icelogs", "icelog", "icepalm", "iceoaklogs", "coal", "ice"]
    total_ice_materials = 0
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(ice_key in k for ice_key in ice_items):
                total_ice_materials += x

    ice_creatures = ["icerat", "icebat", "icecrab", "icegoblin", "ice"]
    ice_kills = count_attack_actions(traj_json, ice_creatures)
    crafted_items = count_crafted_items(traj_json)

    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    ice_materials_passed = total_ice_materials >= 50
    ice_kills_passed = ice_kills >= 15
    crafted_passed = crafted_items >= 8
    survival_passed = all_alive

    passed = ice_materials_passed and ice_kills_passed and crafted_passed and survival_passed
    msg = f"Ice materials: {total_ice_materials}/50, Kills: {ice_kills}/15, Crafts: {crafted_items}/8, Alive: {all_alive}"
    return (1 if passed else 0, msg)


def task_67_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Biome Resource Caravan - 80+ resources, 12+ crafted items."""
    inventories = get_final_inventories(traj_json)
    
    resource_keys = ["logs", "oak", "palm", "ice", "stick", "coal", "ironore", "goldore",
                     "rawshrimp", "rawtuna", "jellyfish", "crab", "fish", "herb", "apple",
                     "peach", "blueberry", "corn", "tomato", "cactus", "feather", "string", "bead"]
    crafted_keys = ["ironbar", "goldbar", "sword", "axe", "pickaxe", "bow", "arrow",
                    "cookedshrimp", "cookedtuna", "ring", "staff", "armor", "boots"]
    starting_items = ["flask", "apple"]

    total_resources = 0
    total_crafted = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in starting_items:
                continue
            is_resource = any(res in k for res in resource_keys)
            is_crafted = any(craft in k for craft in crafted_keys)
            if is_resource:
                total_resources += x
            elif is_crafted:
                total_crafted += x

    resources_passed = total_resources >= 80
    crafted_passed = total_crafted >= 12

    passed = resources_passed and crafted_passed
    msg = f"Resources: {total_resources}/80, Crafted: {total_crafted}/12"
    return (1 if passed else 0, msg)


def task_71_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Region Supply Network - 40+ iron bars, 20+ gold bars, 10+ weapons, 7+ rings."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    iron_bars = item_counts.get("ironbar", 0)
    gold_bars = item_counts.get("goldbar", 0)
    weapons = (item_counts.get("sword", 0) + item_counts.get("sword1", 0) +
               item_counts.get("sword2", 0) + item_counts.get("heavysword", 0) +
               item_counts.get("axe", 0) + item_counts.get("bow", 0))
    rings = (item_counts.get("goldring", 0) + item_counts.get("ring", 0) +
             item_counts.get("silverring", 0))

    iron_passed = iron_bars >= 40
    gold_passed = gold_bars >= 20
    weapons_passed = weapons >= 10
    rings_passed = rings >= 7

    passed = iron_passed and gold_passed and weapons_passed and rings_passed
    msg = f"Iron bars: {iron_bars}/40, Gold bars: {gold_bars}/20, Weapons: {weapons}/10, Rings: {rings}/7"
    return (1 if passed else 0, msg)


def task_75_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Continental Relief Convoy - 30+ iron bars, 30+ cooked shrimp, 60+ arrows, all HP > 25%."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    ironbar = item_counts.get("ironbar", 0)
    cookedshrimp = item_counts.get("cookedshrimp", 0)
    arrow = item_counts.get("arrow", 0)

    agent_hp = get_final_agent_status(traj_json)
    all_healthy = True
    for agent, hp_data in agent_hp.items():
        percent = (hp_data['current'] / hp_data['max'] * 100) if hp_data['max'] > 0 else 0
        if percent <= 25:
            all_healthy = False

    ironbar_passed = ironbar >= 30
    shrimp_passed = cookedshrimp >= 30
    arrow_passed = arrow >= 60
    hp_passed = all_healthy

    passed = ironbar_passed and shrimp_passed and arrow_passed and hp_passed
    msg = f"Iron bars: {ironbar}/30, Cooked shrimp: {cookedshrimp}/30, Arrows: {arrow}/60, HP>25%: {hp_passed}"
    return (1 if passed else 0, msg)


def task_78_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Transcontinental Trading Network - craft 5 specific items."""
    inventories = get_final_inventories(traj_json)
    
    all_items = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            all_items[k] = all_items.get(k, 0) + x

    golden_bow = all_items.get("goldenbow", 0)
    beryl_pendant = all_items.get("berylpendant", 0) + all_items.get("pendant", 0)
    golden_ring = all_items.get("goldring", 0) + all_items.get("goldenring", 0)
    silver_ring = all_items.get("silverring", 0)
    magic_staff = all_items.get("magicstaff", 0)

    bow_passed = golden_bow >= 1
    pendant_passed = beryl_pendant >= 1
    goldring_passed = golden_ring >= 1
    silverring_passed = silver_ring >= 1
    staff_passed = magic_staff >= 1

    passed = bow_passed and pendant_passed and goldring_passed and silverring_passed and staff_passed
    msg = f"Golden Bow: {golden_bow}/1, Beryl Pendant: {beryl_pendant}/1, Golden Ring: {golden_ring}/1, Silver Ring: {silver_ring}/1, Magic Staff: {magic_staff}/1"
    return (1 if passed else 0, msg)


def task_80_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Festival Preparation - 10+ food, 4+ rings, 3+ decorations."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cooked_food_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                        "cookedmeat", "jellyfishsmoothie", "stew"]
    cooked_food = sum(item_counts.get(k, 0) for k in cooked_food_keys)

    silver_rings = item_counts.get("silverring", 0)
    golden_rings = item_counts.get("goldring", 0) + item_counts.get("goldenring", 0)
    total_rings = silver_rings + golden_rings

    pendant_keys = ["berylpendant", "topazpendant", "emeraldpendant", "pendant"]
    pendants = sum(item_counts.get(k, 0) for k in pendant_keys)
    staffs = item_counts.get("magicstaff", 0) + item_counts.get("staff", 0) + item_counts.get("lightningstaff", 0)
    decorations = pendants + staffs

    food_passed = cooked_food >= 10
    rings_passed = total_rings >= 4
    decor_passed = decorations >= 3

    passed = food_passed and rings_passed and decor_passed
    msg = f"Food: {cooked_food}/10, Rings: {total_rings}/4, Decorations: {decorations}/3"
    return (1 if passed else 0, msg)


def task_82_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Royal Evacuation Command - all agents survive."""
    agent_hp = get_final_agent_status(traj_json)
    all_alive = all(hp['current'] > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_83_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Relay Ritual - craft all 4 elemental cores."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    berylpendant = item_counts.get("berylpendant", 0)
    goldring = item_counts.get("goldring", 0) + item_counts.get("goldenring", 0)
    cookedtuna = item_counts.get("cookedtuna", 0)
    lightningstaff = item_counts.get("lightningstaff", 0)

    earth_passed = berylpendant >= 1
    flame_passed = goldring >= 1
    tide_passed = cookedtuna >= 1
    gale_passed = lightningstaff >= 1

    passed = earth_passed and flame_passed and tide_passed and gale_passed
    msg = f"Earth(berylpendant): {berylpendant}/1, Flame(goldring): {goldring}/1, Tide(cookedtuna): {cookedtuna}/1, Gale(lightningstaff): {lightningstaff}/1"
    return (1 if passed else 0, msg)


def task_85_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Frostveil Lifeline Convoy - all agents survive."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    msg = f"All agents alive: {all_alive}"
    return (1 if all_alive else 0, msg)


def task_92_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Continental Trade Network - multiple production targets."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cookedshrimp = item_counts.get("cookedshrimp", 0)
    jellyfishsmoothie = item_counts.get("jellyfishsmoothie", 0)
    ironbar = item_counts.get("ironbar", 0)
    goldbar = item_counts.get("goldbar", 0)
    goldring = item_counts.get("goldring", 0)
    heavysword = item_counts.get("heavysword", 0) + item_counts.get("sword2", 0)
    axe = item_counts.get("axe", 0)

    shrimp_passed = cookedshrimp >= 20
    smoothie_passed = jellyfishsmoothie >= 8
    iron_passed = ironbar >= 15
    gold_passed = goldbar >= 8
    ring_passed = goldring >= 3
    sword_passed = heavysword >= 2
    axe_passed = axe >= 2

    passed = (shrimp_passed and smoothie_passed and iron_passed and
              gold_passed and ring_passed and sword_passed and axe_passed)
    msg = f"Shrimp: {cookedshrimp}/20, Smoothie: {jellyfishsmoothie}/8, Iron: {ironbar}/15, Gold: {goldbar}/8, Rings: {goldring}/3, Swords: {heavysword}/2, Axes: {axe}/2"
    return (1 if passed else 0, msg)


def task_94_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Maritime Trading Empire - 30+ seafood, 20+ tools, 30+ luxury, 80+ total."""
    inventories = get_final_inventories(traj_json)
    
    seafood_keys = ["rawshrimp", "shrimp", "jellyfish", "crab", "rawtuna", "tuna", "fish"]
    tool_weapon_keys = ["axe", "sword", "pickaxe", "bow", "arrow", "heavysword", "sword1", "sword2"]
    luxury_keys = ["ring", "goldring", "silverring", "pendant", "staff", "cookedshrimp",
                   "cookedtuna", "jellyfishsmoothie", "emerald", "ruby", "bead"]
    starting_items = ["flask", "apple", "leatherarmor", "leatherboots"]

    seafood_count = 0
    tool_count = 0
    luxury_count = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in starting_items:
                continue
            if any(sf in k for sf in seafood_keys):
                seafood_count += x
            elif any(tw in k for tw in tool_weapon_keys):
                tool_count += x
            elif any(lx in k for lx in luxury_keys):
                luxury_count += x

    total = seafood_count + tool_count + luxury_count

    seafood_passed = seafood_count >= 30
    tool_passed = tool_count >= 20
    luxury_passed = luxury_count >= 30
    total_passed = total >= 80

    passed = seafood_passed and tool_passed and luxury_passed and total_passed
    msg = f"Seafood: {seafood_count}/30, Tools: {tool_count}/20, Luxury: {luxury_count}/30, Total: {total}/80"
    return (1 if passed else 0, msg)


def task_96_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mountain Rescue Operation - 100+ supplies, all survive."""
    inventories = get_final_inventories(traj_json)
    
    supply_items = ["flask", "apple", "cookedshrimp", "healthpotion", "logs", "pickaxe", "axe"]
    total_supplies = 0

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if any(s in k for s in supply_items):
                total_supplies += x

    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False

    supplies_passed = total_supplies >= 100
    survival_passed = all_alive

    passed = supplies_passed and survival_passed
    msg = f"Supplies: {total_supplies}/100, All alive: {all_alive}"
    return (1 if passed else 0, msg)


def task_98_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mining Conglomerate - 120+ ores, 100+ bars, 20+ products."""
    inventories = get_final_inventories(traj_json)
    
    ore_keys = ["ironore", "goldore", "coal"]
    bar_keys = ["ironbar", "goldbar", "bronzebar", "silverbar", "steelbar"]
    product_keys = ["heavysword", "axe", "goldring", "silverring", "pickaxe", "sword", "dagger"]

    ore_totals = {}
    bar_totals = {}
    product_totals = {}

    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in ore_keys:
                ore_totals[k] = ore_totals.get(k, 0) + x
            elif k in bar_keys:
                bar_totals[k] = bar_totals.get(k, 0) + x
            elif k in product_keys:
                product_totals[k] = product_totals.get(k, 0) + x

    total_ores = sum(ore_totals.values())
    total_bars = sum(bar_totals.values())
    total_products = sum(product_totals.values())

    ore_passed = total_ores >= 120
    bar_passed = total_bars >= 100
    product_passed = total_products >= 20

    passed = ore_passed and bar_passed and product_passed
    msg = f"Ores: {total_ores}/120, Bars: {total_bars}/100, Products: {total_products}/20"
    return (1 if passed else 0, msg)


def task_99_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Kingdom Festival Celebration - 30+ food, 20+ masterwork, 60+ total."""
    inventories = get_final_inventories(traj_json)
    
    item_counts = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x

    cooked_keys = ["cookedshrimp", "cookedtuna", "cookedchicken", "cookedbeef",
                   "cookedmeat", "jellyfishsmoothie", "stew"]
    masterwork_keys = ["heavysword", "sword2", "axe", "pickaxe", "bow",
                       "goldring", "goldenring", "silverring",
                       "emeraldpendant", "berylpendant", "topazpendant", "pendant",
                       "magicstaff", "lightningstaff"]
    trophy_keys = ["feather", "bead", "lightningbead", "emerald", "ruby", "beryl",
                   "rawmeat", "rawchicken", "rawbeef"]

    cooked_count = sum(item_counts.get(k, 0) for k in cooked_keys)
    masterwork_count = sum(item_counts.get(k, 0) for k in masterwork_keys)
    trophy_count = sum(item_counts.get(k, 0) for k in trophy_keys)
    total_festival = cooked_count + masterwork_count + trophy_count

    food_passed = cooked_count >= 30
    masterwork_passed = masterwork_count >= 20
    total_passed = total_festival >= 60

    passed = food_passed and masterwork_passed and total_passed
    msg = f"Food: {cooked_count}/30, Masterwork: {masterwork_count}/20, Total: {total_festival}/60"
    return (1 if passed else 0, msg)


# =============================================================================
# MAIN VERIFIER DISPATCH
# =============================================================================

VERIFIERS = {
    # Combat
    'task_16': task_16_verifier,
    'task_28': task_28_verifier,
    'task_29': task_29_verifier,
    'task_30': task_30_verifier,
    'task_35': task_35_verifier,
    'task_36': task_36_verifier,
    'task_50': task_50_verifier,
    'task_55': task_55_verifier,
    'task_72': task_72_verifier,
    'task_77': task_77_verifier,
    'task_88': task_88_verifier,
    'task_91': task_91_verifier,
    
    # Construction
    'task_41': task_41_verifier,
    'task_43': task_43_verifier,
    'task_74': task_74_verifier,
    'task_76': task_76_verifier,
    'task_81': task_81_verifier,
    'task_84': task_84_verifier,
    'task_87': task_87_verifier,
    'task_89': task_89_verifier,
    'task_90': task_90_verifier,
    'task_93': task_93_verifier,
    
    # Crafting
    'task_00': task_00_verifier,
    'task_01': task_01_verifier,
    'task_02': task_02_verifier,
    'task_03': task_03_verifier,
    'task_05': task_05_verifier,
    'task_06': task_06_verifier,
    'task_07': task_07_verifier,
    'task_08': task_08_verifier,
    'task_09': task_09_verifier,
    'task_10': task_10_verifier,
    'task_11': task_11_verifier,
    'task_12': task_12_verifier,
    'task_13': task_13_verifier,
    'task_14': task_14_verifier,
    'task_15': task_15_verifier,
    'task_22': task_22_verifier,
    'task_27': task_27_verifier,
    'task_31': task_31_verifier,
    'task_34': task_34_verifier,
    'task_39': task_39_verifier,
    'task_47': task_47_verifier,
    'task_49': task_49_verifier,
    'task_52': task_52_verifier,
    'task_54': task_54_verifier,
    'task_58': task_58_verifier,
    'task_61': task_61_verifier,
    'task_62': task_62_verifier,
    'task_63': task_63_verifier,
    'task_65': task_65_verifier,
    'task_66': task_66_verifier,
    'task_68': task_68_verifier,
    'task_69': task_69_verifier,
    'task_86': task_86_verifier,
    'task_97': task_97_verifier,
    
    # Exploration
    'task_21': task_21_verifier,
    'task_23': task_23_verifier,
    'task_24': task_24_verifier,
    'task_33': task_33_verifier,
    'task_46': task_46_verifier,
    'task_48': task_48_verifier,
    'task_53': task_53_verifier,
    'task_57': task_57_verifier,
    'task_60': task_60_verifier,
    'task_70': task_70_verifier,
    'task_73': task_73_verifier,
    'task_79': task_79_verifier,
    'task_95': task_95_verifier,
    'task_100': task_100_verifier,
    
    # Specialized tasks from verify/ folder
    'task_17': task_17_verifier,
    'task_18': task_18_verifier,
    'task_19': task_19_verifier,
    'task_20': task_20_verifier,
    'task_25': task_25_verifier,
    'task_26': task_26_verifier,
    'task_32': task_32_verifier,
    'task_37': task_37_verifier,
    'task_38': task_38_verifier,
    'task_40': task_40_verifier,
    'task_42': task_42_verifier,
    'task_44': task_44_verifier,
    'task_45': task_45_verifier,
    'task_51': task_51_verifier,
    'task_56': task_56_verifier,
    'task_59': task_59_verifier,
    'task_64': task_64_verifier,
    'task_67': task_67_verifier,
    'task_71': task_71_verifier,
    'task_75': task_75_verifier,
    'task_78': task_78_verifier,
    'task_80': task_80_verifier,
    'task_82': task_82_verifier,
    'task_83': task_83_verifier,
    'task_85': task_85_verifier,
    'task_92': task_92_verifier,
    'task_94': task_94_verifier,
    'task_96': task_96_verifier,
    'task_98': task_98_verifier,
    'task_99': task_99_verifier,
}


def verify_task(traj_json: Dict, task_id: str = None) -> Tuple[int, str]:
    """Main entry point to verify a task from trajectory."""
    if task_id is None:
        task_id = traj_json.get('task_id', '')
    
    if task_id in VERIFIERS:
        return VERIFIERS[task_id](traj_json)
    else:
        return (0, f"No verifier found for {task_id}")


def main():
    parser = argparse.ArgumentParser(description='Verify AgentWorld task completion')
    parser.add_argument('--traj_path', type=str, required=True, help='Path to trajectory JSON file')
    parser.add_argument('--task_id', type=str, default=None, help='Override task ID (e.g., task_01)')
    args = parser.parse_args()
    
    with open(args.traj_path, 'r') as f:
        traj_json = json.load(f)
    
    # Parse task_id from filename if not provided
    task_id = args.task_id
    if task_id is None:
        task_id = parse_task_id_from_path(args.traj_path)
    if task_id is None:
        task_id = traj_json.get('task_id', 'unknown')
    
    score, msg = verify_task(traj_json, task_id)
    
    print(f"Task: {task_id}")
    print(f"Score: {score}")
    print(f"Details: {msg}")
    
    return score


if __name__ == "__main__":
    main()
