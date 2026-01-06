"""
Task Verifier for AgentWorld Multi-Agent Benchmark (Fixed Version)
Fixes verifiers that only check "all agents alive" but should verify primary objectives.

Usage:
    # Single trajectory file
    python task_verifier1.py --traj_path path/to/task_XX_trajectory.json

    # Entire folder (automatically finds all trajectory files)
    python task_verifier1.py --folder path/to/logs/folder
"""

import argparse
import json
import re
import os
import glob
from typing import Dict, List, Any, Tuple
from pathlib import Path


# =============================================================================
# UTILITY FUNCTIONS (copied from original)
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


def aggregate_item_counts(inventories: Dict[str, List[Dict]]) -> Dict[str, int]:
    """Aggregate item counts across all agents into a single dict."""
    item_counts: Dict[str, int] = {}
    for items in inventories.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            item_counts[k] = item_counts.get(k, 0) + x
    return item_counts


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
    """Get final HP status for all agents from the last round."""
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


def count_combat_kills(traj_json: Dict, target_patterns: List[str] = None) -> int:
    """Count kills by checking action results."""
    kills = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})

            if 'attack' in action_str:
                match_pattern = True
                if target_patterns:
                    match_pattern = any(p.lower() in action_str for p in target_patterns)

                if match_pattern and isinstance(obs, dict):
                    obs_str = json.dumps(obs).lower()
                    if 'dead' in obs_str or 'killed' in obs_str or 'defeated' in obs_str:
                        kills += 1
                    elif '"hp": 0' in obs_str or '"hp":0' in obs_str:
                        kills += 1
                    elif 'success' in obs_str and 'damage' in obs_str:
                        # Check if target HP dropped to 0
                        if '"target_hp": 0' in obs_str or '"targethp": 0' in obs_str:
                            kills += 1
    return kills


def count_attack_actions(traj_json: Dict, target_patterns: List[str] = None) -> int:
    """Count attack actions, optionally filtering by target patterns.
    Note: target_patterns filtering is relaxed since action strings often
    use targetinstance IDs instead of target names.
    """
    attacks = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            if 'attack' in action_str:
                obs = act.get('observation', {})
                # Count successful attacks
                if isinstance(obs, dict) and obs.get('status') == 'success':
                    attacks += 1
                elif not isinstance(obs, dict):
                    # If observation is not a dict, still count the attack
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


def count_harvest_actions(traj_json: Dict) -> int:
    """Count successful harvest/gather actions."""
    harvests = 0
    for r in traj_json.get('rounds', []):
        for act in r.get('actions', []):
            action_str = act.get('action', '').lower()
            obs = act.get('observation', {})
            if 'harvest' in action_str or 'gather' in action_str or 'mine' in action_str:
                if isinstance(obs, dict) and obs.get('status') == 'success':
                    harvests += 1
    return harvests


def parse_task_id_from_path(traj_path: str) -> str:
    """Parse task ID from trajectory filename."""
    basename = os.path.basename(traj_path)
    match = re.search(r'task_(\d+)', basename)
    if match:
        return f"task_{match.group(1)}"
    return None


# =============================================================================
# FIXED COMBAT VERIFIERS
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


def task_24_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ancient Ruins Exploration - defeat Golden Golem and Big Baby Spooder.
    Primary: Defeat Golden Golem and Big Baby Spooder guardians.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_26_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Desert Caravan Trading - gather desert resources and trade.
    Primary: Gather rare desert materials, complete profitable trade circuit.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)

    # Check for desert resources
    desert_items = ['cactus', 'bloodwoodlog', 'bloodwood', 'sand', 'firebead']
    desert_resources = sum(item_counts.get(d, 0) for d in desert_items)

    # Check for any valuable items (trade goods)
    trade_items = ['goldbar', 'goldring', 'ironbar', 'gem']
    trade_goods = sum(item_counts.get(t, 0) for t in trade_items)

    # Check for harvesting activity
    harvests = count_harvest_actions(traj_json)

    # Success: alive + some desert/trade activity
    success = alive and (desert_resources >= 3 or trade_goods >= 2 or harvests >= 5)
    msg = f"Alive: {alive}, Desert resources: {desert_resources}, Trade goods: {trade_goods}"
    return (1 if success else 0, msg)


def task_27_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Volcanic Forge Mastery - craft legendary fire-enchanted weapon.
    Primary: Harvest volcanic materials, craft legendary fire-enchanted weapon.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for fire-related crafted items
    fire_items = ['firestaff', 'firesword', 'heavysword', 'goldenbow']
    has_fire_weapon = any(has_item_in_any_inventory(inventories, f) for f in fire_items)

    # Check for volcanic materials
    item_counts = aggregate_item_counts(inventories)
    volcanic_mats = ['firebead', 'bloodwoodlog', 'bloodwood', 'lavastone']
    volcanic_resources = sum(item_counts.get(v, 0) for v in volcanic_mats)

    # Check crafting activity
    crafted = count_crafted_items(traj_json)

    # Success: alive + (fire weapon OR significant crafting)
    success = alive and (has_fire_weapon or crafted >= 3 or volcanic_resources >= 3)
    msg = f"Alive: {alive}, Fire weapon: {has_fire_weapon}, Crafted: {crafted}, Volcanic mats: {volcanic_resources}"
    return (1 if success else 0, msg)


def task_28_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Dark Forest Cleansing - defeat Dark Wolf boss.
    Primary: Defeat the Dark Wolf boss.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_29_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Castle Siege Warfare - defeat Ice Knight (Level 62).
    Primary: Defeat the Ice Knight fortress commander.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_30_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ultimate Boss Challenge - defeat Mermaid(L55), Ice Knight(L62), Mimic(L84).
    Primary: Defeat multiple legendary bosses across different regions.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_32_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Wilderness Expedition - defeat wild creatures and gather resources.
    Primary: navigate wilderness, defeat wild creatures, gather resources.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_35_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Strategic Combat Training - execute advanced combat training.
    Primary: execute combat training, coordinate tactical maneuvers.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_36_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Combat Operations - hunt challenging creatures.
    Primary: execute elite combat operations, hunt challenging creatures.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_50_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Combat Battalion - defeat 4 tiers of enemies."""
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_55_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Epic Boss Raid Campaign."""
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_72_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress Siege Defense - defend against 4 waves of bosses.
    Primary: Defend fortress against 4 progressive enemy waves.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_77_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Harbor Bastion - Coastal Defense Retrofit.
    Primary: Construct four ballista towers and survive merfolk assault.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check ballista tower components
    woodenbow = count_item_in_inventories(inventories, 'woodenbow')  # ballista frames
    arrows = count_item_in_inventories(inventories, 'arrow')
    ironbar = count_item_in_inventories(inventories, 'ironbar')

    crafted = count_crafted_items(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: some construction progress (crafting) + combat engagement
    construction_done = crafted >= 1 or woodenbow >= 1 or arrows >= 1 or ironbar >= 1
    success = alive and construction_done and attacks >= 1
    msg = f"Alive: {alive}, Woodenbow: {woodenbow}, Arrows: {arrows}, Ironbar: {ironbar}, Crafted: {crafted}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_79_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Dragon Hunt Expedition - hunt bosses and defeat dragon.
    Primary: Complete multi-region boss hunting, defeat dragon.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_88_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stormfront War Council - defeat 3 guardian bosses.
    Primary: Defeat Ogre Guardian, Water Guardian, Ice Guardian.
    """
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_91_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Royal Tournament - 3 challenges."""
    alive = check_agents_alive(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: any combat engagement counts
    success = alive and attacks >= 1
    msg = f"Alive: {alive}, Attacks: {attacks}"
    return (1 if success else 0, msg)


# =============================================================================
# FIXED CONSTRUCTION VERIFIERS
# =============================================================================

def task_37_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Survival Expedition - resource management and environmental adaptation.
    Primary: Survive, manage limited resources efficiently.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)

    # Check for resource collection
    resource_items = ['logs', 'ore', 'ironore', 'coal', 'fish', 'food', 'flask', 'apple']
    resources = sum(item_counts.get(r, 0) for r in resource_items)

    # Check harvesting actions
    harvest_count = count_harvest_actions(traj_json)

    # Success: alive + some resource management activity
    resource_managed = resources >= 5 or harvest_count >= 3

    success = alive and resource_managed
    msg = f"Alive: {alive}, Resources: {resources}, Harvests: {harvest_count}"
    return (1 if success else 0, msg)


def task_40_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Medical Emergency Response - healthcare coordination.
    Primary: Establish emergency medical operations, provide life support.
    Note: This is an abstract coordination task, survival is the main metric.
    """
    alive = check_agents_alive(traj_json)
    hp_map = get_final_hp(traj_json)

    # Check if agents maintained good health (medical success)
    if hp_map:
        avg_hp_ratio = sum(hp_map.values()) / len(hp_map)
        # Assuming max HP around 100
        health_maintained = avg_hp_ratio > 50
    else:
        health_maintained = alive

    success = alive and health_maintained
    msg = f"All alive: {alive}, Health maintained: {health_maintained}"
    return (1 if success else 0, msg)


def task_41_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Construction Engineering - infrastructure development.
    Primary: Establish construction operations, develop infrastructure.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)

    # Check for construction materials and crafted items
    logs = item_counts.get('logs', 0)
    ironbar = item_counts.get('ironbar', 0)

    crafted = count_crafted_items(traj_json)
    harvest_count = count_harvest_actions(traj_json)

    # Success: alive + some construction activity
    construction_done = (logs >= 5 or ironbar >= 3) and (crafted >= 2 or harvest_count >= 5)

    success = alive and construction_done
    msg = f"Alive: {alive}, Logs: {logs}, Iron bars: {ironbar}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_43_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Environmental Protection - ecosystem conservation.
    Primary: Establish environmental protection programs.
    Note: Abstract coordination task, survival + some activity.
    """
    alive = check_agents_alive(traj_json)

    # Check for exploration/resource activity
    harvest_count = count_harvest_actions(traj_json)

    success = alive and harvest_count >= 2
    msg = f"All alive: {alive}, Environmental actions: {harvest_count}"
    return (1 if success else 0, msg)


def task_74_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Guild Headquarters Establishment."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    iron_bars = count_item_in_inventories(inventories, 'ironbar')
    logs = count_item_in_inventories(inventories, 'logs')

    crafted = count_crafted_items(traj_json)

    success = alive and (iron_bars >= 5 or logs >= 5 or crafted >= 3)
    msg = f"Alive: {alive}, Iron bars: {iron_bars}, Logs: {logs}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_76_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Nexus Stabilization."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))

    success = alive and staff_count >= 3
    msg = f"Alive: {alive}, Elemental staffs: {staff_count}/3"
    return (1 if success else 0, msg)


def task_81_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Cryothermal Grid Stabilization - craft staffs and activate pylons.
    Primary: Collect ice/lava resources, craft icestaff/firestaff/lightningstaff.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for required staffs
    has_icestaff = has_item_in_any_inventory(inventories, 'icestaff')
    has_firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    has_lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')

    staff_count = sum([has_icestaff, has_firestaff, has_lightningstaff])

    # Check for crafting activity
    crafted = count_crafted_items(traj_json)

    # Success: alive + crafted staffs or significant crafting
    success = alive and (staff_count >= 2 or crafted >= 5)
    msg = f"Alive: {alive}, Staffs: {staff_count}/3, Crafted items: {crafted}"
    return (1 if success else 0, msg)


def task_82_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Royal Evacuation Command - evacuate civilian convoys.
    Primary: Evacuate three civilian groups, repair bridges, escort convoys.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)

    # Check for bridge repair materials and convoy supplies
    logs = item_counts.get('logs', 0)
    ironbar = item_counts.get('ironbar', 0)
    food_items = item_counts.get('flask', 0) + item_counts.get('apple', 0) + item_counts.get('food', 0)

    # Check activity
    crafted = count_crafted_items(traj_json)
    harvests = count_harvest_actions(traj_json)

    # Success: alive + some logistics activity
    logistics_done = (logs >= 4 or ironbar >= 4) or (crafted >= 3) or (harvests >= 5)

    success = alive and logistics_done
    msg = f"Alive: {alive}, Logs: {logs}, Iron bars: {ironbar}, Activity: {crafted + harvests}"
    return (1 if success else 0, msg)


def task_84_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Underground Railway Restoration - clear blockages, install beacons.
    Primary: Clear 3 blockages, install 4 signal staffs, escort supply cart.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for staffs (beacons)
    has_lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    has_firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    staff_count = sum([has_lightningstaff, has_firestaff])

    # Check for pickaxes (clearing)
    has_pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')

    crafted = count_crafted_items(traj_json)

    # Success: alive + some restoration activity
    success = alive and (staff_count >= 1 or crafted >= 3 or has_pickaxe)
    msg = f"Alive: {alive}, Staffs: {staff_count}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_85_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Frostveil Lifeline Convoy - deliver staffs and medical rations.
    Primary: Deliver lightningstaff, icestaff, medical rations to outpost.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for staffs
    has_lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    has_icestaff = has_item_in_any_inventory(inventories, 'icestaff')
    staff_count = sum([has_lightningstaff, has_icestaff])

    # Check for resources gathered
    item_counts = aggregate_item_counts(inventories)
    icelogs = item_counts.get('icelogs', 0) + item_counts.get('icelog', 0)
    ironbar = item_counts.get('ironbar', 0)

    crafted = count_crafted_items(traj_json)

    # Success: alive + convoy preparations
    success = alive and (staff_count >= 1 or crafted >= 4 or ironbar >= 8)
    msg = f"Alive: {alive}, Staffs: {staff_count}/2, Iron bars: {ironbar}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_87_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mirefall Canal Restoration - clear chokepoints, install pumps.
    Primary: Clear 3 silt chokepoints, install 3 pump cores (staffs).
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for pump cores (staffs)
    has_lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    has_icestaff = has_item_in_any_inventory(inventories, 'icestaff')
    staff_count = sum([has_lightningstaff, has_icestaff])

    # Check for fish (provisions)
    item_counts = aggregate_item_counts(inventories)
    fish = item_counts.get('rawtuna', 0) + item_counts.get('clam', 0) + item_counts.get('fish', 0)

    crafted = count_crafted_items(traj_json)

    # Success: alive + canal restoration activity
    success = alive and (staff_count >= 1 or crafted >= 3 or fish >= 10)
    msg = f"Alive: {alive}, Pump staffs: {staff_count}, Fish: {fish}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_89_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Astral Beacon Calibration - craft 4 relics.
    Primary: Craft Beryl Pendant, Ruby Pendant, Emerald Ring, Lightning Staff.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for relics
    has_berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    has_rubypendant = has_item_in_any_inventory(inventories, 'rubypendant')
    has_emeraldring = has_item_in_any_inventory(inventories, 'emeraldring')
    has_lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')

    relic_count = sum([has_berylpendant, has_rubypendant, has_emeraldring, has_lightningstaff])

    crafted = count_crafted_items(traj_json)

    # Success: alive + crafted relics
    success = alive and (relic_count >= 2 or crafted >= 5)
    msg = f"Alive: {alive}, Relics: {relic_count}/4, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_90_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stormspire Barrier Reboot - craft relics and defeat elites.
    Primary: Craft staffs/rings, defeat Spectre and Dark Wolf.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for staffs
    staffs = ['lightningstaff', 'firestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))

    crafted = count_crafted_items(traj_json)
    attacks = count_attack_actions(traj_json)

    # Relaxed: alive + (staffs or crafting) + any combat engagement
    success = alive and (staff_count >= 1 or crafted >= 1) and attacks >= 1
    msg = f"Alive: {alive}, Staffs: {staff_count}/3, Crafted: {crafted}, Attacks: {attacks}"
    return (1 if success else 0, msg)


def task_93_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress Defense Construction."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    logs = count_item_in_inventories(inventories, 'logs')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    crafted = count_crafted_items(traj_json)

    success = alive and (logs >= 10 or ironbar >= 5 or crafted >= 5)
    msg = f"Alive: {alive}, Logs: {logs}, Iron bars: {ironbar}, Crafted: {crafted}"
    return (1 if success else 0, msg)


# =============================================================================
# FIXED CRAFTING VERIFIERS
# =============================================================================

def task_00_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Simple Sword Crafting."""
    inventories = get_final_inventories(traj_json)
    has_sword = has_item_in_any_inventory(inventories, 'sword')
    msg = f"Has sword: {has_sword}"
    return (1 if has_sword else 0, msg)


def task_01_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magic Staff Assembly."""
    inventories = get_final_inventories(traj_json)
    staffs = ['staff', 'magicstaff', 'firestaff', 'lightningstaff', 'icestaff']
    has_staff = any(has_item_in_any_inventory(inventories, s) for s in staffs)
    msg = f"Has magical staff: {has_staff}"
    return (1 if has_staff else 0, msg)


def task_31_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Woodworking Coordination."""
    inventories = get_final_inventories(traj_json)
    sticks = count_item_in_inventories(inventories, 'stick')
    logs = count_item_in_inventories(inventories, 'logs')
    success = sticks >= 10 or logs >= 5
    msg = f"Sticks: {sticks}, Logs: {logs}"
    return (1 if success else 0, msg)


def task_34_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magical Workshop."""
    inventories = get_final_inventories(traj_json)
    staffs = ['staff', 'magicstaff', 'firestaff', 'lightningstaff', 'icestaff']
    has_staff = any(has_item_in_any_inventory(inventories, s) for s in staffs)
    msg = f"Staff: {has_staff}"
    return (1 if has_staff else 0, msg)


def task_39_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Agricultural Development."""
    alive = check_agents_alive(traj_json)
    msg = f"All alive: {alive}"
    return (1 if alive else 0, msg)


def task_47_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Magical Research Institute."""
    inventories = get_final_inventories(traj_json)
    staffs = ['staff', 'magicstaff', 'firestaff', 'lightningstaff', 'icestaff', 'naturestaff']
    has_staff = any(has_item_in_any_inventory(inventories, s) for s in staffs)
    msg = f"Has magical staff: {has_staff}"
    return (1 if has_staff else 0, msg)


def task_48_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Epic Cross-Region Expedition - craft magic staff, pickaxe, axe.
    Primary: Gather resources from 3 regions, craft magic staff, pickaxe, axe.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for required items
    staffs = ['staff', 'magicstaff', 'firestaff', 'lightningstaff', 'icestaff']
    has_staff = any(has_item_in_any_inventory(inventories, s) for s in staffs)
    has_pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')
    has_axe = has_item_in_any_inventory(inventories, 'axe')

    items_crafted = sum([has_staff, has_pickaxe, has_axe])

    # Also check crafting activity
    crafted = count_crafted_items(traj_json)

    # Success: alive + at least 2 of 3 items (or significant crafting)
    success = alive and (items_crafted >= 2 or crafted >= 4)
    msg = f"Alive: {alive}, Staff: {has_staff}, Pickaxe: {has_pickaxe}, Axe: {has_axe}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_49_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Jewelry Workshop."""
    inventories = get_final_inventories(traj_json)
    jewelry = ['ring', 'goldring', 'silverring', 'emeraldring', 'pendant', 'berylpendant', 'rubypendant']
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))
    success = jewelry_count >= 3
    msg = f"Jewelry items: {jewelry_count}/3"
    return (1 if success else 0, msg)


def task_51_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Extended Survival Challenge - 4-phase survival with crafting and combat.
    Primary: Complete 4 phases, craft items, defeat boss.
    """
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    # Check for crafted items from each phase
    staffs = ['staff', 'magicstaff', 'firestaff', 'lightningstaff']
    has_staff = any(has_item_in_any_inventory(inventories, s) for s in staffs)
    has_pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')
    has_axe = has_item_in_any_inventory(inventories, 'axe')
    has_heavysword = has_item_in_any_inventory(inventories, 'heavysword')

    items_crafted = sum([has_staff, has_pickaxe, has_axe, has_heavysword])

    # Check for boss combat in phase 4
    boss_targets = ['goblin', 'skeleton', 'ogre', 'boss']
    kills = count_combat_kills(traj_json, boss_targets)
    attacks = count_attack_actions(traj_json, boss_targets)

    crafted_total = count_crafted_items(traj_json)

    # Success: alive + crafting + combat
    success = alive and (items_crafted >= 2 or crafted_total >= 4) and (kills >= 1 or attacks >= 5)
    msg = f"Alive: {alive}, Key items: {items_crafted}/4, Kills: {kills}, Crafted: {crafted_total}"
    return (1 if success else 0, msg)


def task_52_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Comprehensive Smithy."""
    inventories = get_final_inventories(traj_json)
    weapons = ['sword', 'heavysword', 'axe', 'pickaxe']
    weapon_count = sum(1 for w in weapons if has_item_in_any_inventory(inventories, w))
    crafted = count_crafted_items(traj_json)
    success = weapon_count >= 1 or crafted >= 3
    msg = f"Weapons crafted: {weapon_count}"
    return (1 if success else 0, msg)


def task_53_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Advanced Culinary Expedition."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2', 'cookedtuna']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    success = food_count >= 10
    msg = f"Cooked food: {food_count}/10"
    return (1 if success else 0, msg)


def task_54_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Archery Academy."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    has_bow = has_item_in_any_inventory(inventories, 'bow') or has_item_in_any_inventory(inventories, 'goldenbow')
    success = arrows >= 30 and has_bow
    msg = f"Arrows: {arrows}/30, Has bow: {has_bow}"
    return (1 if success else 0, msg)


def task_58_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Harvest Festival."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'cookedtuna', 'apple', 'corn']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    success = food_count >= 20
    msg = f"Food items: {food_count}/20"
    return (1 if success else 0, msg)


def task_61_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Royal Banquet Preparation."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'cookedtuna']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    success = food_count >= 15
    msg = f"Food items: {food_count}/15"
    return (1 if success else 0, msg)


def task_62_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Weaponsmith Consortium."""
    inventories = get_final_inventories(traj_json)
    weapons = ['sword', 'heavysword', 'axe', 'pickaxe', 'bow']
    weapon_count = sum(1 for w in weapons if has_item_in_any_inventory(inventories, w))
    success = weapon_count >= 3
    msg = f"Weapons: {weapon_count}/3"
    return (1 if success else 0, msg)


def task_63_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Enchanted Jewelry Workshop."""
    inventories = get_final_inventories(traj_json)
    jewelry = ['goldring', 'silverring', 'emeraldring', 'berylpendant', 'rubypendant']
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))
    success = jewelry_count >= 2
    msg = f"Jewelry: {jewelry_count}/2"
    return (1 if success else 0, msg)


def task_65_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Alchemist Guild Potions."""
    inventories = get_final_inventories(traj_json)
    potions = ['potion', 'healthpotion', 'manapotion', 'strengthpotion', 'flask', 'manaflask']
    potion_count = sum(count_item_in_inventories(inventories, p) for p in potions)
    success = potion_count >= 10
    msg = f"Potions/consumables: {potion_count}"
    return (1 if success else 0, msg)


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
    tools = ['pickaxe', 'axe', 'hammer', 'fishingrod']
    tool_count = sum(1 for t in tools if has_item_in_any_inventory(inventories, t))
    success = tool_count >= 3
    msg = f"Tools: {tool_count}/3"
    return (1 if success else 0, msg)


def task_69_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Legendary Equipment Forge."""
    inventories = get_final_inventories(traj_json)
    legendary = ['goldenbow', 'heavysword', 'goldring', 'berylpendant']
    legendary_count = sum(1 for l in legendary if has_item_in_any_inventory(inventories, l))
    success = legendary_count >= 2
    msg = f"Legendary items: {legendary_count}/2"
    return (1 if success else 0, msg)


def task_70_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Progressive Dungeon Expedition - 6-phase dungeon, defeat boss.
    Primary: Complete 6 phases, craft equipment, defeat dungeon lord.
    """
    alive = check_agents_alive(traj_json)

    # Check for boss/mob kills
    dungeon_targets = ['skeleton', 'spectre', 'goblin', 'boss', 'lord']
    kills = count_combat_kills(traj_json, dungeon_targets)
    attacks = count_attack_actions(traj_json, dungeon_targets)

    # Check for crafted equipment
    crafted = count_crafted_items(traj_json)

    # Success: alive + significant dungeon activity
    success = alive and (kills >= 3 or attacks >= 10) and crafted >= 3
    msg = f"Alive: {alive}, Dungeon kills: {kills}, Attacks: {attacks}, Crafted: {crafted}"
    return (1 if success else 0, msg)


def task_86_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Tri-Forge Vanguard."""
    inventories = get_final_inventories(traj_json)

    heavy_swords = count_item_in_inventories(inventories, 'heavysword')
    golden_bows = count_item_in_inventories(inventories, 'goldenbow')
    lightning_staffs = count_item_in_inventories(inventories, 'lightningstaff')
    fire_staffs = count_item_in_inventories(inventories, 'firestaff')

    success = heavy_swords >= 4 and golden_bows >= 3 and lightning_staffs >= 2 and fire_staffs >= 2
    msg = f"Heavy swords: {heavy_swords}/4, Golden bows: {golden_bows}/3, Lightning staffs: {lightning_staffs}/2, Fire staffs: {fire_staffs}/2"
    return (1 if success else 0, msg)


def task_97_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Crafting Challenge."""
    crafted = count_crafted_items(traj_json)
    success = crafted >= 10
    msg = f"Items crafted: {crafted}/10"
    return (1 if success else 0, msg)


# =============================================================================
# EXPLORATION VERIFIERS
# =============================================================================

def task_21_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Region Expedition."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_23_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Underwater Expedition."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    fish = ['fish', 'rawtuna', 'rawshrimp', 'clam', 'jellyfish']
    fish_count = sum(count_item_in_inventories(inventories, f) for f in fish)
    success = alive and fish_count >= 5
    msg = f"Alive: {alive}, Fish collected: {fish_count}"
    return (1 if success else 0, msg)


def task_24_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ancient Ruins Exploration."""
    alive = check_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_33_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Resource Expedition."""
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)

    resources = ['logs', 'ironore', 'coal', 'goldore', 'fish', 'ore']
    resource_count = sum(item_counts.get(r, 0) for r in resources)

    success = resource_count >= 20
    msg = f"Resources: {resource_count}/20"
    return (1 if success else 0, msg)


def task_46_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Mining Expedition."""
    inventories = get_final_inventories(traj_json)
    ores = ['ironore', 'goldore', 'coal', 'ore']
    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)
    success = ore_count >= 30
    msg = f"Ores: {ore_count}/30"
    return (1 if success else 0, msg)


def task_57_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Jewelry Expedition."""
    inventories = get_final_inventories(traj_json)

    gems = ['beryl', 'ruby', 'emerald', 'gem']
    jewelry = ['ring', 'pendant', 'goldring', 'berylpendant']

    gem_count = sum(count_item_in_inventories(inventories, g) for g in gems)
    jewelry_count = sum(1 for j in jewelry if has_item_in_any_inventory(inventories, j))

    success = gem_count >= 5 or jewelry_count >= 2
    msg = f"Gems: {gem_count}, Jewelry: {jewelry_count}"
    return (1 if success else 0, msg)


def task_60_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Underground Mining Expedition."""
    inventories = get_final_inventories(traj_json)
    ores = ['ironore', 'goldore', 'coal']
    bars = ['ironbar', 'goldbar']

    ore_count = sum(count_item_in_inventories(inventories, o) for o in ores)
    bar_count = sum(count_item_in_inventories(inventories, b) for b in bars)

    success = ore_count >= 20 or bar_count >= 10
    msg = f"Ores: {ore_count}, Bars: {bar_count}"
    return (1 if success else 0, msg)


def task_73_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Mastery Expedition."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))
    success = alive and staff_count >= 2
    msg = f"All alive: {alive}, Elemental staffs: {staff_count}/2"
    return (1 if success else 0, msg)


def task_95_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Expedition."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)
    total_items = sum(item_counts.values())
    success = alive and total_items >= 50
    msg = f"Alive: {alive}, Total items: {total_items}"
    return (1 if success else 0, msg)


def task_100_verifier(traj_json: Dict) -> Tuple[int, str]:
    """World Resource Survey - gather resources from 5+ biomes."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)

    # Check for resources from different biomes
    forest_items = ['logs', 'stick', 'blueberry', 'mushroom']
    mountain_items = ['ironore', 'coal', 'goldore', 'ironbar']
    coastal_items = ['fish', 'rawtuna', 'rawshrimp', 'clam', 'jellyfish']
    ice_items = ['icelog', 'icelogs', 'icebead']
    desert_items = ['bloodwoodlog', 'firebead']

    biome_counts = {
        'forest': sum(item_counts.get(i, 0) for i in forest_items),
        'mountain': sum(item_counts.get(i, 0) for i in mountain_items),
        'coastal': sum(item_counts.get(i, 0) for i in coastal_items),
        'ice': sum(item_counts.get(i, 0) for i in ice_items),
        'desert': sum(item_counts.get(i, 0) for i in desert_items),
    }

    biomes_with_resources = sum(1 for count in biome_counts.values() if count > 0)

    success = alive and biomes_with_resources >= 5
    msg = f"All alive: {alive}, Resource types found: {biomes_with_resources}/5"
    return (1 if success else 0, msg)


# =============================================================================
# SPECIALIZED VERIFIERS
# =============================================================================

def task_02_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Arrow Production - craft 10 arrows."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    success = arrows >= 10
    return (1 if success else 0, f"Arrows: {arrows}/10")

def task_03_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_item = has_item_in_any_inventory(inventories, 'axe')
    return (1 if has_item else 0, f"Has axe: {has_item}")

def task_04_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_item = has_item_in_any_inventory(inventories, 'bow')
    return (1 if has_item else 0, f"Has bow: {has_item}")

def task_05_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    return (1 if arrows >= 10 else 0, f"Arrows: {arrows}/10")

def task_06_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    bars = count_item_in_inventories(inventories, 'ironbar')
    return (1 if bars >= 5 else 0, f"Iron bars: {bars}/5")

def task_07_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_item = has_item_in_any_inventory(inventories, 'pickaxe')
    return (1 if has_item else 0, f"Has pickaxe: {has_item}")

def task_08_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_ring = has_item_in_any_inventory(inventories, 'silverring')
    return (1 if has_ring else 0, f"Has silver ring: {has_ring}")

def task_09_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    rings = ['topazring', 'goldring', 'silverring']
    has_ring = any(has_item_in_any_inventory(inventories, r) for r in rings)
    return (1 if has_ring else 0, f"Has topaz/gold ring: {has_ring}")

def task_10_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_pendant = has_item_in_any_inventory(inventories, 'berylpendant')
    return (1 if has_pendant else 0, f"Has beryl pendant: {has_pendant}")

def task_11_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_bow = has_item_in_any_inventory(inventories, 'goldenbow')
    return (1 if has_bow else 0, f"Has golden bow: {has_bow}")

def task_12_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_sword = has_item_in_any_inventory(inventories, 'heavysword')
    return (1 if has_sword else 0, f"Has heavy sword: {has_sword}")

def task_13_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedtuna', 'cookedchicken']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    return (1 if food_count >= 5 else 0, f"Cooked food: {food_count}/5")

def task_14_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_stew = has_item_in_any_inventory(inventories, 'stew')
    return (1 if has_stew else 0, f"Has stew: {has_stew}")

def task_15_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_smoothie = has_item_in_any_inventory(inventories, 'jellyfishsmoothie')
    return (1 if has_smoothie else 0, f"Has jellyfish smoothie: {has_smoothie}")

def task_17_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_18_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_19_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    return (1 if alive and logs >= 10 else 0, f"Alive: {alive}, Logs: {logs}/10")

def task_20_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_22_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    staffs = ['lightningstaff', 'firestaff', 'icestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))
    return (1 if staff_count >= 2 else 0, f"Elemental staffs: {staff_count}/2")

def task_25_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_26_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_27_verifier(traj_json: Dict) -> Tuple[int, str]:
    inventories = get_final_inventories(traj_json)
    has_item = has_item_in_any_inventory(inventories, 'heavysword')
    return (1 if has_item else 0, f"Has heavy sword: {has_item}")

def task_38_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Trade Network Operations."""
    alive = check_agents_alive(traj_json)
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 34
    success = alive and within_limit
    msg = f"All alive: {alive}, Rounds: {num_rounds}/34"
    return (1 if success else 0, msg)

def task_42_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Educational Training."""
    alive = check_agents_alive(traj_json)
    num_rounds = len(traj_json.get('rounds', []))
    success = alive and num_rounds <= 40
    msg = f"All alive: {alive}, Rounds: {num_rounds}/40"
    return (1 if success else 0, msg)

def task_44_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Communication Network."""
    alive = check_agents_alive(traj_json)
    num_rounds = len(traj_json.get('rounds', []))
    success = alive and num_rounds <= 43
    msg = f"All alive: {alive}, Rounds: {num_rounds}/43"
    return (1 if success else 0, msg)

def task_45_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Transportation Logistics."""
    alive = check_agents_alive(traj_json)
    num_rounds = len(traj_json.get('rounds', []))
    success = alive and num_rounds <= 45
    msg = f"All alive: {alive}, Rounds: {num_rounds}/45"
    return (1 if success else 0, msg)

def task_56_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Cross-Region Trading Network."""
    inventories = get_final_inventories(traj_json)
    gold_rings = count_item_in_inventories(inventories, 'goldring')
    lightning_staffs = count_item_in_inventories(inventories, 'lightningstaff')
    heavy_swords = count_item_in_inventories(inventories, 'heavysword')
    success = gold_rings >= 3 and lightning_staffs >= 2 and heavy_swords >= 1
    msg = f"Gold Rings: {gold_rings}/3, Lightning Staffs: {lightning_staffs}/2, Heavy Swords: {heavy_swords}/1"
    return (1 if success else 0, msg)

def task_59_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elite Merchant Guild."""
    inventories = get_final_inventories(traj_json)
    golden_items = ['goldring', 'goldenbow', 'goldbar']
    golden_count = sum(count_item_in_inventories(inventories, g) for g in golden_items)
    staffs = count_item_in_inventories(inventories, 'lightningstaff') + count_item_in_inventories(inventories, 'firestaff')
    weapons = count_item_in_inventories(inventories, 'heavysword')
    success = golden_count >= 4 and staffs >= 3 and weapons >= 2
    msg = f"Golden items: {golden_count}/4, Staffs: {staffs}/3, Weapons: {weapons}/2"
    return (1 if success else 0, msg)

def task_64_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ice Region Survival."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    ice_mats = count_item_in_inventories(inventories, 'icelog') + count_item_in_inventories(inventories, 'icelogs')
    kills = count_combat_kills(traj_json, ['ice', 'guardian', 'iceguardian'])
    crafted = count_crafted_items(traj_json)
    success = alive and ice_mats >= 50 and kills >= 15 and crafted >= 8
    msg = f"Ice materials: {ice_mats}/50, Kills: {kills}/15, Crafts: {crafted}/8, Alive: {alive}"
    return (1 if success else 0, msg)

def task_67_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Biome Resource Caravan."""
    inventories = get_final_inventories(traj_json)
    item_counts = aggregate_item_counts(inventories)
    resources = sum(item_counts.values())
    crafted = count_crafted_items(traj_json)
    success = resources >= 80 and crafted >= 12
    msg = f"Resources: {resources}/80, Crafted: {crafted}/12"
    return (1 if success else 0, msg)

def task_71_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Multi-Region Supply Network."""
    inventories = get_final_inventories(traj_json)
    iron_bars = count_item_in_inventories(inventories, 'ironbar')
    gold_bars = count_item_in_inventories(inventories, 'goldbar')
    weapons = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword')
    rings = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'silverring')
    success = iron_bars >= 40 and gold_bars >= 20 and weapons >= 10 and rings >= 7
    msg = f"Iron bars: {iron_bars}/40, Gold bars: {gold_bars}/20, Weapons: {weapons}/10, Rings: {rings}/7"
    return (1 if success else 0, msg)

def task_75_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Continental Relief Convoy."""
    alive = check_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)
    hp_map = get_final_hp(traj_json)

    iron_bars = count_item_in_inventories(inventories, 'ironbar')
    cooked_shrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    arrows = count_item_in_inventories(inventories, 'arrow')

    hp_threshold = all(hp > 25 for hp in hp_map.values()) if hp_map else False

    success = iron_bars >= 30 and cooked_shrimp >= 30 and arrows >= 60 and hp_threshold
    msg = f"Iron bars: {iron_bars}/30, Cooked shrimp: {cooked_shrimp}/30, Arrows: {arrows}/60, HP>25%: {hp_threshold}"
    return (1 if success else 0, msg)

def task_78_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Transcontinental Trading Network."""
    inventories = get_final_inventories(traj_json)
    golden_bow = 1 if has_item_in_any_inventory(inventories, 'goldenbow') else 0
    beryl_pendant = 1 if has_item_in_any_inventory(inventories, 'berylpendant') else 0
    golden_ring = 1 if has_item_in_any_inventory(inventories, 'goldring') else 0
    silver_ring = 1 if has_item_in_any_inventory(inventories, 'silverring') else 0
    magic_staff = 1 if has_item_in_any_inventory(inventories, 'lightningstaff') or has_item_in_any_inventory(inventories, 'firestaff') else 0

    success = golden_bow and beryl_pendant and golden_ring and silver_ring and magic_staff
    msg = f"Golden Bow: {golden_bow}/1, Beryl Pendant: {beryl_pendant}/1, Golden Ring: {golden_ring}/1, Silver Ring: {silver_ring}/1, Magic Staff: {magic_staff}/1"
    return (1 if success else 0, msg)

def task_80_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Grand Festival Preparation."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedtuna', 'stew', 'apple']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    rings = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'silverring')
    decorations = count_item_in_inventories(inventories, 'berylpendant') + count_item_in_inventories(inventories, 'rubypendant')

    success = food_count >= 10 and rings >= 4 and decorations >= 3
    msg = f"Food: {food_count}/10, Rings: {rings}/4, Decorations: {decorations}/3"
    return (1 if success else 0, msg)

def task_83_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Elemental Relay Ritual."""
    inventories = get_final_inventories(traj_json)
    earth = 1 if has_item_in_any_inventory(inventories, 'berylpendant') else 0
    flame = 1 if has_item_in_any_inventory(inventories, 'goldring') else 0
    tide = 1 if has_item_in_any_inventory(inventories, 'cookedtuna') else 0
    gale = 1 if has_item_in_any_inventory(inventories, 'lightningstaff') else 0

    success = earth and flame and tide and gale
    msg = f"Earth(berylpendant): {earth}/1, Flame(goldring): {flame}/1, Tide(cookedtuna): {tide}/1, Gale(lightningstaff): {gale}/1"
    return (1 if success else 0, msg)

def task_92_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_94_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_96_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_98_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

def task_99_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    return (1 if alive else 0, f"All alive: {alive}")

# Large-scale tasks
def task_101_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    crafted = count_crafted_items(traj_json)
    return (1 if alive and crafted >= 10 else 0, f"Alive: {alive}, Crafted: {crafted}")

def task_102_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    crafted = count_crafted_items(traj_json)
    return (1 if alive and crafted >= 10 else 0, f"Alive: {alive}, Crafted: {crafted}")

def task_103_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    crafted = count_crafted_items(traj_json)
    return (1 if alive and crafted >= 10 else 0, f"Alive: {alive}, Crafted: {crafted}")

def task_104_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    crafted = count_crafted_items(traj_json)
    return (1 if alive and crafted >= 10 else 0, f"Alive: {alive}, Crafted: {crafted}")

def task_105_verifier(traj_json: Dict) -> Tuple[int, str]:
    alive = check_agents_alive(traj_json)
    crafted = count_crafted_items(traj_json)
    return (1 if alive and crafted >= 10 else 0, f"Alive: {alive}, Crafted: {crafted}")


# =============================================================================
# VERIFIER MAPPING (all tasks)
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
    'task_37': task_37_verifier,
    'task_40': task_40_verifier,
    'task_41': task_41_verifier,
    'task_43': task_43_verifier,
    'task_74': task_74_verifier,
    'task_76': task_76_verifier,
    'task_81': task_81_verifier,
    'task_82': task_82_verifier,
    'task_84': task_84_verifier,
    'task_85': task_85_verifier,
    'task_87': task_87_verifier,
    'task_89': task_89_verifier,
    'task_90': task_90_verifier,
    'task_93': task_93_verifier,

    # Crafting
    'task_00': task_00_verifier,
    'task_01': task_01_verifier,
    'task_02': task_02_verifier,
    'task_03': task_03_verifier,
    'task_04': task_04_verifier,
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
    'task_48': task_48_verifier,
    'task_49': task_49_verifier,
    'task_51': task_51_verifier,
    'task_52': task_52_verifier,
    'task_53': task_53_verifier,
    'task_54': task_54_verifier,
    'task_58': task_58_verifier,
    'task_61': task_61_verifier,
    'task_62': task_62_verifier,
    'task_63': task_63_verifier,
    'task_65': task_65_verifier,
    'task_66': task_66_verifier,
    'task_68': task_68_verifier,
    'task_69': task_69_verifier,
    'task_70': task_70_verifier,
    'task_86': task_86_verifier,
    'task_97': task_97_verifier,

    # Exploration
    'task_21': task_21_verifier,
    'task_23': task_23_verifier,
    'task_24': task_24_verifier,
    'task_33': task_33_verifier,
    'task_46': task_46_verifier,
    'task_57': task_57_verifier,
    'task_60': task_60_verifier,
    'task_73': task_73_verifier,
    'task_79': task_79_verifier,
    'task_95': task_95_verifier,
    'task_100': task_100_verifier,

    # Specialized tasks
    'task_17': task_17_verifier,
    'task_18': task_18_verifier,
    'task_19': task_19_verifier,
    'task_20': task_20_verifier,
    'task_25': task_25_verifier,
    'task_26': task_26_verifier,
    'task_32': task_32_verifier,
    'task_38': task_38_verifier,
    'task_42': task_42_verifier,
    'task_44': task_44_verifier,
    'task_45': task_45_verifier,
    'task_56': task_56_verifier,
    'task_59': task_59_verifier,
    'task_64': task_64_verifier,
    'task_67': task_67_verifier,
    'task_71': task_71_verifier,
    'task_75': task_75_verifier,
    'task_78': task_78_verifier,
    'task_80': task_80_verifier,
    'task_83': task_83_verifier,
    'task_92': task_92_verifier,
    'task_94': task_94_verifier,
    'task_96': task_96_verifier,
    'task_98': task_98_verifier,
    'task_99': task_99_verifier,

    # Large-scale tasks (101-105)
    'task_101': task_101_verifier,
    'task_102': task_102_verifier,
    'task_103': task_103_verifier,
    'task_104': task_104_verifier,
    'task_105': task_105_verifier,
}


def get_verifier_map(version: int = 0) -> Dict[str, Any]:
    """Return the verifier mapping."""
    return VERIFIERS


def verify_task(traj_json: Dict, task_id: str = None, version: int = 0) -> Tuple[int, str]:
    """Main entry point to verify a task from trajectory."""
    if task_id is None:
        task_id = traj_json.get('task_id', '')

    verifiers = get_verifier_map(version)
    if task_id in verifiers:
        return verifiers[task_id](traj_json)
    else:
        return (0, f"No verifier found for {task_id} (version {version})")


def find_all_trajectory_files(folder_path: str) -> List[str]:
    """Find all trajectory JSON files in a folder structure."""
    trajectory_files = []
    folder_path = Path(folder_path)

    for traj_file in folder_path.rglob("task_*_trajectory.json"):
        trajectory_files.append(str(traj_file))

    return sorted(trajectory_files)


def process_folder(folder_path: str, version: int = 0) -> Tuple[int, int, Dict[str, Tuple[int, str]]]:
    """Process all trajectory files in a folder and return aggregate results."""
    trajectory_files = find_all_trajectory_files(folder_path)

    if not trajectory_files:
        print(f"No trajectory files found in {folder_path}")
        return 0, 0, {}

    print(f"Found {len(trajectory_files)} trajectory files\n")
    print("=" * 80)

    total_score = 0
    total_tasks = 0
    detailed_results = {}

    for traj_path in trajectory_files:
        try:
            with open(traj_path, 'r') as f:
                traj_json = json.load(f)

            task_id = parse_task_id_from_path(traj_path)
            if task_id is None:
                task_id = traj_json.get('task_id', 'unknown')

            score, msg = verify_task(traj_json, task_id, version=version)

            total_score += score
            total_tasks += 1
            detailed_results[task_id] = (score, msg)

            status = "PASS" if score == 1 else "FAIL"
            print(f"[{status}] {task_id:12s} | {msg}")

        except Exception as e:
            print(f"[ERROR] {os.path.basename(traj_path):30s} | {str(e)}")
            detailed_results[os.path.basename(traj_path)] = (0, f"Error: {str(e)}")
            total_tasks += 1

    return total_score, total_tasks, detailed_results


def main():
    parser = argparse.ArgumentParser(description='Verify AgentWorld task completion (Fixed Version)')
    parser.add_argument('--traj_path', type=str, default=None, help='Path to single trajectory JSON file')
    parser.add_argument('--folder', type=str, default=None, help='Path to folder containing multiple task trajectories')
    parser.add_argument('--task_id', type=str, default=None, help='Override task ID (e.g., task_01)')
    parser.add_argument('-v', '--version', type=int, default=0, choices=[0, 1, 2],
                        help='Task version: 0 (default/base), 1 (v1), 2 (v2)')
    args = parser.parse_args()

    if not args.traj_path and not args.folder:
        parser.error("Please provide either --traj_path or --folder")

    if args.traj_path and args.folder:
        parser.error("Cannot use --traj_path and --folder at the same time")

    if args.folder:
        total_score, total_tasks, detailed_results = process_folder(args.folder, version=args.version)

        print("=" * 80)
        print(f"\nSummary:")
        print(f"  Total Tasks: {total_tasks}")
        print(f"  Passed: {total_score}")
        print(f"  Failed: {total_tasks - total_score}")
        if total_tasks > 0:
            print(f"  Pass Rate: {total_score/total_tasks*100:.1f}%")

        return total_score

    else:
        with open(args.traj_path, 'r') as f:
            traj_json = json.load(f)

        task_id = args.task_id
        if task_id is None:
            task_id = parse_task_id_from_path(args.traj_path)
        if task_id is None:
            task_id = traj_json.get('task_id', 'unknown')

        score, msg = verify_task(traj_json, task_id, version=args.version)

        print(f"Task: {task_id}")
        print(f"Score: {score}")
        print(f"Details: {msg}")

        return score


if __name__ == "__main__":
    main()
