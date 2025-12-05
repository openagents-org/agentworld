"""
Task Verifier for AgentWorld Multi-Agent Benchmark - V1 Variant Tasks
Covers: task_00_v1 to task_105_v1

Usage:
    python task_verifier_v1.py --traj_path path/to/task_XX_v1_trajectory.json

The task ID is automatically parsed from the filename (e.g., task_10_v1_trajectory.json -> task_10_v1)
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


def get_final_agent_hp(traj_json: Dict) -> Dict[str, int]:
    """Get final HP for all agents."""
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


def check_all_agents_alive(traj_json: Dict) -> bool:
    """Check if all agents survived (HP > 0 in final state)."""
    agent_hp = get_final_agent_hp(traj_json)
    if not agent_hp:
        return True
    return all(hp > 0 for hp in agent_hp.values())


def parse_task_id_from_path(traj_path: str) -> str:
    """Parse task ID from trajectory filename."""
    basename = os.path.basename(traj_path)
    match = re.search(r'task_(\d+)_v1', basename)
    if match:
        return f"task_{match.group(1)}_v1"
    return None


# =============================================================================
# V1 TASK VERIFIERS (task_00_v1 to task_105_v1)
# =============================================================================

def task_00_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete all three major crafting projects: staff, 10 arrows, silver ring."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    arrows = count_item_in_inventories(inventories, 'arrow')
    silverring = has_item_in_any_inventory(inventories, 'silverring')

    success = staff and arrows >= 10 and silverring
    msg = f"Staff: {staff}, Arrows: {arrows}/10, Silver ring: {silverring}"
    return (1 if success else 0, msg)


def task_01_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare wizard_agent with crafted magic staff for magical combat."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    msg = f"Staff crafted: {staff}"
    return (1 if staff else 0, msg)


def task_02_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Produce a batch of 10 arrows."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    success = arrows >= 10
    msg = f"Arrows: {arrows}/10"
    return (1 if success else 0, msg)


def task_03_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a silver ring."""
    inventories = get_final_inventories(traj_json)
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    msg = f"Silver ring: {silverring}"
    return (1 if silverring else 0, msg)


def task_04_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create an axe."""
    inventories = get_final_inventories(traj_json)
    axe = has_item_in_any_inventory(inventories, 'axe')
    msg = f"Axe crafted: {axe}"
    return (1 if axe else 0, msg)


def task_05_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a beryl pendant."""
    inventories = get_final_inventories(traj_json)
    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    msg = f"Beryl pendant: {berylpendant}"
    return (1 if berylpendant else 0, msg)


def task_06_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge a heavy sword."""
    inventories = get_final_inventories(traj_json)
    heavysword = has_item_in_any_inventory(inventories, 'sword2') or has_item_in_any_inventory(inventories, 'heavysword')
    msg = f"Heavy sword: {heavysword}"
    return (1 if heavysword else 0, msg)


def task_07_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge a high-quality pickaxe."""
    inventories = get_final_inventories(traj_json)
    pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')
    msg = f"Pickaxe: {pickaxe}"
    return (1 if pickaxe else 0, msg)


def task_08_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create bronze bars."""
    inventories = get_final_inventories(traj_json)
    bronzebar = has_item_in_any_inventory(inventories, 'bronzebar')
    msg = f"Bronze bar: {bronzebar}"
    return (1 if bronzebar else 0, msg)


def task_09_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a topaz ring."""
    inventories = get_final_inventories(traj_json)
    topazring = has_item_in_any_inventory(inventories, 'topazring')
    msg = f"Topaz ring: {topazring}"
    return (1 if topazring else 0, msg)


def task_10_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare a delicious stew."""
    inventories = get_final_inventories(traj_json)
    stew = has_item_in_any_inventory(inventories, 'stew') or has_item_in_any_inventory(inventories, 'stew2')
    msg = f"Stew: {stew}"
    return (1 if stew else 0, msg)


def task_11_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a fire staff through magic staff creation and elemental enhancement."""
    inventories = get_final_inventories(traj_json)
    firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    msg = f"Fire staff: {firestaff}"
    return (1 if firestaff else 0, msg)


def task_12_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a gold ring."""
    inventories = get_final_inventories(traj_json)
    goldring = has_item_in_any_inventory(inventories, 'goldring')
    msg = f"Gold ring: {goldring}"
    return (1 if goldring else 0, msg)


def task_13_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a utility bucket."""
    inventories = get_final_inventories(traj_json)
    bucket = has_item_in_any_inventory(inventories, 'bucket')
    msg = f"Bucket: {bucket}"
    return (1 if bucket else 0, msg)


def task_14_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare cooked shrimp through simple cooking operations."""
    inventories = get_final_inventories(traj_json)
    cookedshrimp = has_item_in_any_inventory(inventories, 'cookedshrimp')
    msg = f"Cooked shrimp: {cookedshrimp}"
    return (1 if cookedshrimp else 0, msg)


def task_15_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a jellyfish smoothie."""
    inventories = get_final_inventories(traj_json)
    smoothie = has_item_in_any_inventory(inventories, 'jellyfishsmoothie')
    msg = f"Jellyfish smoothie: {smoothie}"
    return (1 if smoothie else 0, msg)


def task_16_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Protect collectors while gathering 3x logs and 2x blueberry."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_all_agents_alive(traj_json)

    success = logs >= 3 and blueberry >= 2 and alive
    msg = f"Logs: {logs}/3, Blueberry: {blueberry}/2, All alive: {alive}"
    return (1 if success else 0, msg)


def task_17_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 3x palmlogs and 3x peach."""
    inventories = get_final_inventories(traj_json)
    palmlogs = count_item_in_inventories(inventories, 'palmlogs')
    peach = count_item_in_inventories(inventories, 'peach')

    success = palmlogs >= 3 and peach >= 3
    msg = f"Palmlogs: {palmlogs}/3, Peach: {peach}/3"
    return (1 if success else 0, msg)


def task_18_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 4x rawshrimp and 2x icelogs."""
    inventories = get_final_inventories(traj_json)
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    icelogs = count_item_in_inventories(inventories, 'icelogs')

    success = rawshrimp >= 4 and icelogs >= 2
    msg = f"Rawshrimp: {rawshrimp}/4, Icelogs: {icelogs}/2"
    return (1 if success else 0, msg)


def task_19_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Protect farmer while gathering 4x corn and 2x tomato."""
    inventories = get_final_inventories(traj_json)
    corn = count_item_in_inventories(inventories, 'corn')
    tomato = count_item_in_inventories(inventories, 'tomato')

    success = corn >= 4 and tomato >= 2
    msg = f"Corn: {corn}/4, Tomato: {tomato}/2"
    return (1 if success else 0, msg)


def task_20_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Protect collectors while gathering 4x blueberry and 3x peach."""
    inventories = get_final_inventories(traj_json)
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    peach = count_item_in_inventories(inventories, 'peach')

    success = blueberry >= 4 and peach >= 3
    msg = f"Blueberry: {blueberry}/4, Peach: {peach}/3"
    return (1 if success else 0, msg)


def task_21_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Smelt gold ore and craft a golden ring with pre-gathered materials."""
    inventories = get_final_inventories(traj_json)
    goldring = has_item_in_any_inventory(inventories, 'goldring')
    msg = f"Gold ring: {goldring}"
    return (1 if goldring else 0, msg)


def task_22_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat the Ice Wizard in coordinated magical combat."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_23_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest 4x jellyfish and 3x clam."""
    inventories = get_final_inventories(traj_json)
    jellyfish = count_item_in_inventories(inventories, 'jellyfish')
    clam = count_item_in_inventories(inventories, 'clam')

    success = jellyfish >= 4 and clam >= 3
    msg = f"Jellyfish: {jellyfish}/4, Clam: {clam}/3"
    return (1 if success else 0, msg)


def task_24_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Explore ancient ruins and defeat the Golden Golem guardian."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_25_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest 4x Ice Oak logs from frozen biome."""
    inventories = get_final_inventories(traj_json)
    ice_logs = count_item_in_inventories(inventories, 'icelogs') + \
               count_item_in_inventories(inventories, 'iceoaklogs')
    alive = check_all_agents_alive(traj_json)

    success = ice_logs >= 4 and alive
    msg = f"Ice logs: {ice_logs}/4, All alive: {alive}"
    return (1 if success else 0, msg)


def task_26_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 4x cactus materials and 3x desert ore."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_27_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest 4x volcanic ore from volcanic region."""
    inventories = get_final_inventories(traj_json)
    volcanite = count_item_in_inventories(inventories, 'volcanite')
    alive = check_all_agents_alive(traj_json)

    success = volcanite >= 4 and alive
    msg = f"Volcanic ore: {volcanite}/4, All alive: {alive}"
    return (1 if alive else 0, msg)


def task_28_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat the Dark Wolf boss in the dark forest."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_29_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Conduct castle reconnaissance and map fortress defenses."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_30_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat the Mermaid (Level 55) boss in coordinated combat."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_31_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest 4x logs and craft 8x sticks."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    sticks = count_item_in_inventories(inventories, 'stick')

    success = logs >= 4 or sticks >= 8
    msg = f"Logs: {logs}/4, Sticks: {sticks}/8"
    return (1 if success else 0, msg)


def task_32_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 3 Worker Ants through coordinated combat."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_33_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 6x logs through coordinated lumberjacking."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    success = logs >= 6
    msg = f"Logs: {logs}/6"
    return (1 if success else 0, msg)


def task_34_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 3x beryl gems and 4x logs."""
    inventories = get_final_inventories(traj_json)
    beryl = count_item_in_inventories(inventories, 'beryl')
    logs = count_item_in_inventories(inventories, 'logs')

    success = beryl >= 3 and logs >= 4
    msg = f"Beryl: {beryl}/3, Logs: {logs}/4"
    return (1 if success else 0, msg)


def task_35_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 2 Worker Ants through coordinated combat training."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_36_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 5 Worker Ants through elite combat coordination."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_37_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 5x apple and 3x blueberry for team survival."""
    inventories = get_final_inventories(traj_json)
    apple = count_item_in_inventories(inventories, 'apple')
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_all_agents_alive(traj_json)

    success = apple >= 5 and blueberry >= 3 and alive
    msg = f"Apple: {apple}/5, Blueberry: {blueberry}/3, Alive: {alive}"
    return (1 if success else 0, msg)


def task_38_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 5x logs and 3x coal for trade preparation."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    coal = count_item_in_inventories(inventories, 'coal')

    success = logs >= 5 and coal >= 3
    msg = f"Logs: {logs}/5, Coal: {coal}/3"
    return (1 if success else 0, msg)


def task_39_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 4x corn and 3x apple through foraging."""
    inventories = get_final_inventories(traj_json)
    corn = count_item_in_inventories(inventories, 'corn')
    apple = count_item_in_inventories(inventories, 'apple')

    success = corn >= 4 and apple >= 3
    msg = f"Corn: {corn}/4, Apple: {apple}/3"
    return (1 if success else 0, msg)


def task_40_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Ensure both agents maintain high health through resource sharing."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_41_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 6x logs and 4x coal for construction projects."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    coal = count_item_in_inventories(inventories, 'coal')

    success = logs >= 6 and coal >= 4
    msg = f"Logs: {logs}/6, Coal: {coal}/4"
    return (1 if success else 0, msg)


def task_42_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Practice foraging and lumberjacking by gathering resources."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_43_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 6x apple and 4x blueberry sustainably."""
    inventories = get_final_inventories(traj_json)
    apple = count_item_in_inventories(inventories, 'apple')
    blueberry = count_item_in_inventories(inventories, 'blueberry')

    success = apple >= 6 and blueberry >= 4
    msg = f"Apple: {apple}/6, Blueberry: {blueberry}/4"
    return (1 if success else 0, msg)


def task_44_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 4x logs and 4x coal, then share between agents."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    coal = count_item_in_inventories(inventories, 'coal')

    success = logs >= 4 and coal >= 4
    msg = f"Logs: {logs}/4, Coal: {coal}/4"
    return (1 if success else 0, msg)


def task_45_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather and transport 3x logs and 3x coal to destination agent."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    coal = count_item_in_inventories(inventories, 'coal')

    success = logs >= 3 and coal >= 3
    msg = f"Logs: {logs}/3, Coal: {coal}/3"
    return (1 if success else 0, msg)


def task_46_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mine resources and smelt 6x iron bars."""
    inventories = get_final_inventories(traj_json)
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    success = ironbar >= 6
    msg = f"Iron bars: {ironbar}/6"
    return (1 if success else 0, msg)


def task_47_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather materials and craft 1x magic staff."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    msg = f"Staff: {staff}"
    return (1 if staff else 0, msg)


def task_48_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete forest expedition: gather 6x logs and craft 1x magic staff."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    staff = has_item_in_any_inventory(inventories, 'staff')

    success = logs >= 6 and staff
    msg = f"Logs: {logs}/6, Staff: {staff}"
    return (1 if success else 0, msg)


def task_49_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Smelt iron bars and craft 2x silver rings."""
    inventories = get_final_inventories(traj_json)
    silverring = count_item_in_inventories(inventories, 'silverring')
    success = silverring >= 2
    msg = f"Silver rings: {silverring}/2"
    return (1 if success else 0, msg)


def task_50_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Form elite combat battalion to defeat three enemies in progressive difficulty."""
    agent_hp = get_final_agent_hp(traj_json)
    survivors = sum(1 for hp in agent_hp.values() if hp > 0)
    total = len(agent_hp) if agent_hp else 5
    success = survivors >= 4
    msg = f"Survivors: {survivors}/{total}"
    return (1 if success else 0, msg)


def task_51_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete survival challenge with resource gathering, crafting, and combat over 40 rounds."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_52_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish four-smith metalworking operation producing tools and weapons."""
    inventories = get_final_inventories(traj_json)
    weapons = ['sword1', 'sword2', 'heavysword', 'axe', 'pickaxe']
    weapon_count = sum(count_item_in_inventories(inventories, w) for w in weapons)
    success = weapon_count >= 4
    msg = f"Weapons/tools: {weapon_count}/4"
    return (1 if success else 0, msg)


def task_53_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete culinary expedition gathering ingredients and producing food items."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    success = food_count >= 5
    msg = f"Cooked food: {food_count}/5"
    return (1 if success else 0, msg)


def task_54_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish archery academy: gather 30+ logs, craft 80+ arrows, produce 6+ bows."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    arrows = count_item_in_inventories(inventories, 'arrow')
    bows = count_item_in_inventories(inventories, 'woodenbow') + count_item_in_inventories(inventories, 'bow')

    success = logs >= 30 and arrows >= 80 and bows >= 6
    msg = f"Logs: {logs}/30, Arrows: {arrows}/80, Bows: {bows}/6"
    return (1 if success else 0, msg)


def task_55_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete 5-phase boss raid campaign with 3 boss battles."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_56_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 2x Golden Rings, 1x Lightning Staff, 1x Heavy Sword."""
    inventories = get_final_inventories(traj_json)
    goldring = count_item_in_inventories(inventories, 'goldring')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')

    success = goldring >= 2 and lightningstaff >= 1 and heavysword >= 1
    msg = f"Gold Rings: {goldring}/2, Lightning Staff: {lightningstaff}/1, Heavy Sword: {heavysword}/1"
    return (1 if success else 0, msg)


def task_57_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create 2x Ruby Rings, 1x Emerald Pendant, 1x Beryl Pendant."""
    inventories = get_final_inventories(traj_json)
    rubyring = count_item_in_inventories(inventories, 'rubyring')
    emeraldpendant = count_item_in_inventories(inventories, 'emeraldpendant')
    berylpendant = count_item_in_inventories(inventories, 'berylpendant')

    success = rubyring >= 2 and emeraldpendant >= 1 and berylpendant >= 1
    msg = f"Ruby Rings: {rubyring}/2, Emerald Pendant: {emeraldpendant}/1, Beryl Pendant: {berylpendant}/1"
    return (1 if success else 0, msg)


def task_58_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare festival package: 3x cooked dishes, 2x decorative jewelry, 30+ gathered resources."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    jewelry = ['silverring', 'goldring', 'berylpendant', 'emeraldpendant']
    jewelry_count = sum(count_item_in_inventories(inventories, j) for j in jewelry)

    success = food_count >= 3 and jewelry_count >= 2
    msg = f"Food: {food_count}/3, Jewelry: {jewelry_count}/2"
    return (1 if success else 0, msg)


def task_59_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 2x Golden items, 2x Staffs, 1x Specialty weapon."""
    inventories = get_final_inventories(traj_json)

    golden = ['goldensword', 'goldenbow', 'goldring']
    golden_count = sum(count_item_in_inventories(inventories, g) for g in golden)

    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(count_item_in_inventories(inventories, s) for s in staffs)

    weapons = ['heavysword', 'sword2', 'pickaxe']
    weapon_count = sum(count_item_in_inventories(inventories, w) for w in weapons)

    success = golden_count >= 2 and staff_count >= 2 and weapon_count >= 1
    msg = f"Golden items: {golden_count}/2, Staffs: {staff_count}/2, Weapons: {weapon_count}/1"
    return (1 if success else 0, msg)


def task_60_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Extract 50+ ores, smelt 40+ bars, craft 6+ metal items."""
    inventories = get_final_inventories(traj_json)

    ores = count_item_in_inventories(inventories, 'ironore') + \
           count_item_in_inventories(inventories, 'goldore') + \
           count_item_in_inventories(inventories, 'coal')
    bars = count_item_in_inventories(inventories, 'ironbar') + \
           count_item_in_inventories(inventories, 'goldbar')

    items = ['pickaxe', 'axe', 'sword1', 'sword2', 'goldring', 'silverring']
    item_count = sum(count_item_in_inventories(inventories, i) for i in items)

    success = ores >= 50 and bars >= 40 and item_count >= 6
    msg = f"Ores: {ores}/50, Bars: {bars}/40, Items: {item_count}/6"
    return (1 if success else 0, msg)


def task_61_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare royal banquet: 8+ cooked dishes, 4+ specialty items, 60+ rare ingredients."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'stew', 'stew2', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    success = food_count >= 8
    msg = f"Cooked dishes: {food_count}/8"
    return (1 if success else 0, msg)


def task_62_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge 5 swords (including golden), 3 axes, 2 bows, 1 pickaxe = 11+ weapons."""
    inventories = get_final_inventories(traj_json)

    swords = count_item_in_inventories(inventories, 'sword1') + \
             count_item_in_inventories(inventories, 'sword2') + \
             count_item_in_inventories(inventories, 'heavysword') + \
             count_item_in_inventories(inventories, 'goldensword')
    axes = count_item_in_inventories(inventories, 'axe')
    bows = count_item_in_inventories(inventories, 'bow') + count_item_in_inventories(inventories, 'woodenbow')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')

    total = swords + axes + bows + pickaxe
    success = swords >= 5 and axes >= 3 and bows >= 2 and pickaxe >= 1
    msg = f"Swords: {swords}/5, Axes: {axes}/3, Bows: {bows}/2, Pickaxe: {pickaxe}/1"
    return (1 if success else 0, msg)


def task_63_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create jewelry collection: 8+ pieces including 3 rings, 3 pendants, 2 base items."""
    inventories = get_final_inventories(traj_json)

    rings = count_item_in_inventories(inventories, 'silverring') + \
            count_item_in_inventories(inventories, 'goldring') + \
            count_item_in_inventories(inventories, 'topazring')
    pendants = count_item_in_inventories(inventories, 'berylpendant') + \
               count_item_in_inventories(inventories, 'emeraldpendant') + \
               count_item_in_inventories(inventories, 'rubypendant')

    total = rings + pendants
    success = rings >= 3 and pendants >= 3 and total >= 8
    msg = f"Rings: {rings}/3, Pendants: {pendants}/3, Total: {total}/8"
    return (1 if success else 0, msg)


def task_64_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 30+ ice materials, hunt 8+ ice creatures, craft 5+ cold-weather items."""
    inventories = get_final_inventories(traj_json)

    ice_items = ['icelogs', 'iceoaklogs']
    ice_count = sum(count_item_in_inventories(inventories, i) for i in ice_items)
    alive = check_all_agents_alive(traj_json)

    success = ice_count >= 30 and alive
    msg = f"Ice materials: {ice_count}/30, All alive: {alive}"
    return (1 if success else 0, msg)


def task_65_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Brew 6+ different consumables including healing, food, and specialty items."""
    inventories = get_final_inventories(traj_json)

    consumables = ['healthpotion', 'manapotion', 'jellyfishsmoothie', 'cookedshrimp', 'cookedchicken', 'stew']
    consumable_count = sum(count_item_in_inventories(inventories, c) for c in consumables)

    success = consumable_count >= 6
    msg = f"Consumables: {consumable_count}/6"
    return (1 if success else 0, msg)


def task_66_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Produce archery arsenal: 30+ arrows, 3+ bows."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    bows = count_item_in_inventories(inventories, 'bow') + count_item_in_inventories(inventories, 'woodenbow')

    success = arrows >= 30 and bows >= 3
    msg = f"Arrows: {arrows}/30, Bows: {bows}/3"
    return (1 if success else 0, msg)


def task_67_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish trading route visiting 4 biomes, gather 50+ resources, craft 8+ regional specialty items."""
    inventories = get_final_inventories(traj_json)

    resources = ['logs', 'coal', 'ironore', 'goldore', 'rawshrimp', 'jellyfish', 'blueberry', 'corn']
    resource_count = sum(count_item_in_inventories(inventories, r) for r in resources)

    crafted = ['ironbar', 'goldbar', 'cookedshrimp', 'arrow', 'sword1', 'axe', 'pickaxe', 'silverring']
    crafted_count = sum(count_item_in_inventories(inventories, c) for c in crafted)

    success = resource_count >= 50 and crafted_count >= 8
    msg = f"Resources: {resource_count}/50, Crafted: {crafted_count}/8"
    return (1 if success else 0, msg)


def task_68_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge 4+ pickaxes, 4+ axes, 3+ buckets for 15+ total implements."""
    inventories = get_final_inventories(traj_json)
    pickaxes = count_item_in_inventories(inventories, 'pickaxe')
    axes = count_item_in_inventories(inventories, 'axe')
    buckets = count_item_in_inventories(inventories, 'bucket')

    total = pickaxes + axes + buckets
    success = pickaxes >= 4 and axes >= 4 and buckets >= 3
    msg = f"Pickaxes: {pickaxes}/4, Axes: {axes}/4, Buckets: {buckets}/3"
    return (1 if success else 0, msg)


def task_69_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge 3+ golden items, 4+ elite weapons."""
    inventories = get_final_inventories(traj_json)

    golden = count_item_in_inventories(inventories, 'goldensword') + \
             count_item_in_inventories(inventories, 'goldenbow') + \
             count_item_in_inventories(inventories, 'goldring')
    elite = count_item_in_inventories(inventories, 'heavysword') + \
            count_item_in_inventories(inventories, 'lightningstaff') + \
            count_item_in_inventories(inventories, 'firestaff')

    success = golden >= 3 and elite >= 4
    msg = f"Golden items: {golden}/3, Elite weapons: {elite}/4"
    return (1 if success else 0, msg)


def task_70_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete 4-phase progressive dungeon expedition over 40 rounds."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_71_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create 3-region supply network with gathering, transport, and crafting over 40 rounds."""
    inventories = get_final_inventories(traj_json)
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    goldbar = count_item_in_inventories(inventories, 'goldbar')

    success = ironbar >= 20 and goldbar >= 10
    msg = f"Iron bars: {ironbar}/20, Gold bars: {goldbar}/10"
    return (1 if success else 0, msg)


def task_72_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defend fortress against 2 progressive enemy waves over 38 rounds."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_73_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete 5-phase elemental mastery journey over 60 rounds."""
    alive = check_all_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))

    success = alive and staff_count >= 2
    msg = f"All alive: {alive}, Elemental staffs: {staff_count}/2"
    return (1 if success else 0, msg)


def task_74_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish guild headquarters over 60 rounds with full equipment for 6 members."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_75_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deliver medical and engineering supplies to coastal refugee pier in 36-38 rounds."""
    inventories = get_final_inventories(traj_json)
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    arrow = count_item_in_inventories(inventories, 'arrow')
    alive = check_all_agents_alive(traj_json)

    success = ironbar >= 20 and cookedshrimp >= 20 and arrow >= 40 and alive
    msg = f"Iron bars: {ironbar}/20, Shrimp: {cookedshrimp}/20, Arrows: {arrow}/40, Alive: {alive}"
    return (1 if success else 0, msg)


def task_76_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stabilize Ice and Stone conduits with catalyst sets and defeat guardians."""
    alive = check_all_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    staffs = ['firestaff', 'lightningstaff', 'icestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))

    success = alive and staff_count >= 2
    msg = f"Alive: {alive}, Staffs: {staff_count}/2"
    return (1 if success else 0, msg)


def task_77_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Construct two ballista towers and survive merfolk assault."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_78_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """6 agents gather resources, travel to hubs, craft 3 items from 3+ regions."""
    inventories = get_final_inventories(traj_json)

    crafted = ['goldenbow', 'berylpendant', 'goldring', 'silverring', 'staff']
    crafted_count = sum(1 for c in crafted if has_item_in_any_inventory(inventories, c))

    success = crafted_count >= 3
    msg = f"Cross-regional items: {crafted_count}/3"
    return (1 if success else 0, msg)


def task_79_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """6 agents travel across 3 biomes, defeat 2-3 bosses, defeat a dragon."""
    agent_hp = get_final_agent_hp(traj_json)
    survivors = sum(1 for hp in agent_hp.values() if hp > 0)
    total = len(agent_hp) if agent_hp else 6
    success = survivors >= total * 0.8
    msg = f"Survivors: {survivors}/{total}"
    return (1 if success else 0, msg)


def task_80_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """6 agents gather resources, cook dishes, craft competition prizes."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedchicken', 'stew', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    rings = count_item_in_inventories(inventories, 'silverring') + count_item_in_inventories(inventories, 'goldring')

    success = food_count >= 8 and rings >= 3
    msg = f"Food: {food_count}/8, Rings: {rings}/3"
    return (1 if success else 0, msg)


def task_81_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stabilize cryothermal grid at 2 locations within 40 rounds."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_82_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Evacuate two civilian groups toward mountains and desert, keep supply wagons intact."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_83_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deliver Earth and Flame cores to Central Obelisk."""
    inventories = get_final_inventories(traj_json)

    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    goldring = has_item_in_any_inventory(inventories, 'goldring')

    success = berylpendant and goldring
    msg = f"Earth (berylpendant): {berylpendant}, Flame (goldring): {goldring}"
    return (1 if success else 0, msg)


def task_84_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Reconnect North Shaft and South Exit, escort supply cart end-to-end."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_85_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deliver convoy manifest (logs, iron bars, lightningstaff, icestaff, rations)."""
    inventories = get_final_inventories(traj_json)

    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    icestaff = has_item_in_any_inventory(inventories, 'icestaff')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    alive = check_all_agents_alive(traj_json)

    success = lightningstaff and icestaff and ironbar >= 10 and alive
    msg = f"Lightning staff: {lightningstaff}, Ice staff: {icestaff}, Iron bars: {ironbar}/10, Alive: {alive}"
    return (1 if success else 0, msg)


def task_86_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 3 heavy swords, 2 golden bows, 1 lightningstaff, 1 firestaff + 25 healing supplies."""
    inventories = get_final_inventories(traj_json)

    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')

    success = heavysword >= 3 and goldenbow >= 2 and lightningstaff >= 1 and firestaff >= 1
    msg = f"Heavy swords: {heavysword}/3, Golden bows: {goldenbow}/2, Lightning: {lightningstaff}/1, Fire: {firestaff}/1"
    return (1 if success else 0, msg)


def task_87_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Reopen Mirefall canal, install pump cores, replenish fish pens, escort supply raft."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_88_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Hold war council, forge war stockpile, defeat Ogre Guardian and Water Guardian."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_89_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 3 attunement relics (Beryl Pendant, Ruby Pendant, Lightning Staff) and install them."""
    inventories = get_final_inventories(traj_json)

    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    rubypendant = has_item_in_any_inventory(inventories, 'rubypendant')
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')

    relics = sum([berylpendant, rubypendant, lightningstaff])
    success = relics >= 3
    msg = f"Beryl pendant: {berylpendant}, Ruby pendant: {rubypendant}, Lightning staff: {lightningstaff}"
    return (1 if success else 0, msg)


def task_90_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft Storm Relic set (3 goldbar pylons, 1 lightningstaff, 1 firestaff, 2 rings), defeat Spectre."""
    inventories = get_final_inventories(traj_json)

    goldbar = count_item_in_inventories(inventories, 'goldbar')
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    rings = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'silverring')
    alive = check_all_agents_alive(traj_json)

    success = goldbar >= 3 and lightningstaff and firestaff and rings >= 2 and alive
    msg = f"Gold bars: {goldbar}/3, Lightning: {lightningstaff}, Fire: {firestaff}, Rings: {rings}/2, Alive: {alive}"
    return (1 if success else 0, msg)


def task_91_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 2+ bosses, craft 4+ equipment items, prepare 15+ food items."""
    inventories = get_final_inventories(traj_json)

    equipment = ['heavysword', 'goldring', 'icestaff', 'silverring', 'axe', 'emeraldpendant']
    equipment_count = sum(1 for e in equipment if has_item_in_any_inventory(inventories, e))

    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'jellyfishsmoothie', 'stew']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    alive = check_all_agents_alive(traj_json)
    success = alive and equipment_count >= 4 and food_count >= 15
    msg = f"Alive: {alive}, Equipment: {equipment_count}/4, Food: {food_count}/15"
    return (1 if success else 0, msg)


def task_92_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish continental trade network with 4 specialized trade hubs over 45 rounds."""
    inventories = get_final_inventories(traj_json)

    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    goldbar = count_item_in_inventories(inventories, 'goldbar')

    success = cookedshrimp >= 15 and ironbar >= 10 and goldbar >= 5
    msg = f"Shrimp: {cookedshrimp}/15, Iron: {ironbar}/10, Gold: {goldbar}/5"
    return (1 if success else 0, msg)


def task_93_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Construct fortress defense system over 50 rounds."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_94_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish maritime trading empire with 3 fishing fleets, 40+ trade goods."""
    inventories = get_final_inventories(traj_json)

    seafood = ['rawshrimp', 'jellyfish', 'cookedshrimp', 'rawtuna']
    trade_goods = ['arrow', 'sword1', 'axe', 'pickaxe', 'goldring', 'silverring']

    seafood_count = sum(count_item_in_inventories(inventories, s) for s in seafood)
    trade_count = sum(count_item_in_inventories(inventories, t) for t in trade_goods)
    total = seafood_count + trade_count

    success = total >= 40
    msg = f"Seafood: {seafood_count}, Trade goods: {trade_count}, Total: {total}/40"
    return (1 if success else 0, msg)


def task_95_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 80+ seafood items, defeat 2+ sea bosses."""
    inventories = get_final_inventories(traj_json)

    seafood = ['rawshrimp', 'jellyfish', 'cookedshrimp', 'rawtuna', 'clam']
    seafood_count = sum(count_item_in_inventories(inventories, s) for s in seafood)

    success = seafood_count >= 80
    msg = f"Seafood: {seafood_count}/80"
    return (1 if success else 0, msg)


def task_96_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Execute mountain rescue across 2 regions, deliver 60+ supplies, establish 2 camps."""
    inventories = get_final_inventories(traj_json)

    supplies = ['flask', 'apple', 'cookedshrimp', 'logs', 'pickaxe']
    supply_count = sum(count_item_in_inventories(inventories, s) for s in supplies)
    alive = check_all_agents_alive(traj_json)

    success = supply_count >= 60 and alive
    msg = f"Supplies: {supply_count}/60, All alive: {alive}"
    return (1 if success else 0, msg)


def task_97_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish agricultural empire producing 80+ food items."""
    inventories = get_final_inventories(traj_json)

    food = ['corn', 'tomato', 'blueberry', 'apple', 'cookedshrimp', 'cookedchicken', 'cookedbeef', 'rawshrimp']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    success = food_count >= 80
    msg = f"Food items: {food_count}/80"
    return (1 if success else 0, msg)


def task_98_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish mining conglomerate: 2 mine sites, 50+ bars, 10+ finished products."""
    inventories = get_final_inventories(traj_json)

    bars = count_item_in_inventories(inventories, 'ironbar') + count_item_in_inventories(inventories, 'goldbar')

    products = ['heavysword', 'axe', 'goldring', 'silverring', 'pickaxe', 'sword1']
    product_count = sum(count_item_in_inventories(inventories, p) for p in products)

    success = bars >= 50 and product_count >= 10
    msg = f"Bars: {bars}/50, Products: {product_count}/10"
    return (1 if success else 0, msg)


def task_99_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare kingdom festival with 3 exhibition arenas, 35+ prepared items."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedtuna', 'cookedchicken', 'jellyfishsmoothie', 'stew']
    crafted = ['heavysword', 'axe', 'goldring', 'silverring', 'berylpendant', 'lightningstaff']

    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    crafted_count = sum(count_item_in_inventories(inventories, c) for c in crafted)
    total = food_count + crafted_count

    success = total >= 35
    msg = f"Food: {food_count}, Crafted: {crafted_count}, Total: {total}/35"
    return (1 if success else 0, msg)


def task_100_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete world resource survey: 6+ regions, 80+ documented findings, 4+ observation posts."""
    inventories = get_final_inventories(traj_json)

    resources = ['logs', 'ironore', 'coal', 'goldore', 'blueberry', 'corn', 'rawshrimp']
    total = sum(count_item_in_inventories(inventories, r) for r in resources)
    found_types = sum(1 for r in resources if count_item_in_inventories(inventories, r) > 0)
    alive = check_all_agents_alive(traj_json)

    success = total >= 80 and found_types >= 6 and alive
    msg = f"Resources: {total}/80, Types: {found_types}/6, Alive: {alive}"
    return (1 if success else 0, msg)


def task_101_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Construct Citadel Foundation: gather resources, process materials, secure perimeter."""
    inventories = get_final_inventories(traj_json)

    ironbar = count_item_in_inventories(inventories, 'ironbar')
    logs = count_item_in_inventories(inventories, 'logs')
    alive = check_all_agents_alive(traj_json)

    success = ironbar >= 30 and logs >= 30 and alive
    msg = f"Iron bars: {ironbar}/30, Logs: {logs}/30, Alive: {alive}"
    return (1 if success else 0, msg)


def task_102_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 3 Fire Staffs, 3 Ice Staffs, 3 Nature Staffs."""
    inventories = get_final_inventories(traj_json)

    firestaff = count_item_in_inventories(inventories, 'firestaff')
    icestaff = count_item_in_inventories(inventories, 'icestaff')
    naturestaff = count_item_in_inventories(inventories, 'naturestaff')

    success = firestaff >= 3 and icestaff >= 3 and naturestaff >= 3
    msg = f"Fire: {firestaff}/3, Ice: {icestaff}/3, Nature: {naturestaff}/3"
    return (1 if success else 0, msg)


def task_103_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Escort all 8 Settlers to Castle Throne Room while neutralizing Ice Knight threats."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_104_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Secure Northern Border (Ice Guardians) and Eastern Border (Golden Golems)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_105_v1_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Produce 3 Golden Bows and 1 Golden Sword."""
    inventories = get_final_inventories(traj_json)

    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    goldensword = count_item_in_inventories(inventories, 'goldensword')
    alive = check_all_agents_alive(traj_json)

    success = goldenbow >= 3 and goldensword >= 1 and alive
    msg = f"Golden bows: {goldenbow}/3, Golden swords: {goldensword}/1, Alive: {alive}"
    return (1 if success else 0, msg)


# =============================================================================
# VERIFIER REGISTRY
# =============================================================================

VERIFIERS = {
    'task_00_v1': task_00_v1_verifier,
    'task_01_v1': task_01_v1_verifier,
    'task_02_v1': task_02_v1_verifier,
    'task_03_v1': task_03_v1_verifier,
    'task_04_v1': task_04_v1_verifier,
    'task_05_v1': task_05_v1_verifier,
    'task_06_v1': task_06_v1_verifier,
    'task_07_v1': task_07_v1_verifier,
    'task_08_v1': task_08_v1_verifier,
    'task_09_v1': task_09_v1_verifier,
    'task_10_v1': task_10_v1_verifier,
    'task_11_v1': task_11_v1_verifier,
    'task_12_v1': task_12_v1_verifier,
    'task_13_v1': task_13_v1_verifier,
    'task_14_v1': task_14_v1_verifier,
    'task_15_v1': task_15_v1_verifier,
    'task_16_v1': task_16_v1_verifier,
    'task_17_v1': task_17_v1_verifier,
    'task_18_v1': task_18_v1_verifier,
    'task_19_v1': task_19_v1_verifier,
    'task_20_v1': task_20_v1_verifier,
    'task_21_v1': task_21_v1_verifier,
    'task_22_v1': task_22_v1_verifier,
    'task_23_v1': task_23_v1_verifier,
    'task_24_v1': task_24_v1_verifier,
    'task_25_v1': task_25_v1_verifier,
    'task_26_v1': task_26_v1_verifier,
    'task_27_v1': task_27_v1_verifier,
    'task_28_v1': task_28_v1_verifier,
    'task_29_v1': task_29_v1_verifier,
    'task_30_v1': task_30_v1_verifier,
    'task_31_v1': task_31_v1_verifier,
    'task_32_v1': task_32_v1_verifier,
    'task_33_v1': task_33_v1_verifier,
    'task_34_v1': task_34_v1_verifier,
    'task_35_v1': task_35_v1_verifier,
    'task_36_v1': task_36_v1_verifier,
    'task_37_v1': task_37_v1_verifier,
    'task_38_v1': task_38_v1_verifier,
    'task_39_v1': task_39_v1_verifier,
    'task_40_v1': task_40_v1_verifier,
    'task_41_v1': task_41_v1_verifier,
    'task_42_v1': task_42_v1_verifier,
    'task_43_v1': task_43_v1_verifier,
    'task_44_v1': task_44_v1_verifier,
    'task_45_v1': task_45_v1_verifier,
    'task_46_v1': task_46_v1_verifier,
    'task_47_v1': task_47_v1_verifier,
    'task_48_v1': task_48_v1_verifier,
    'task_49_v1': task_49_v1_verifier,
    'task_50_v1': task_50_v1_verifier,
    'task_51_v1': task_51_v1_verifier,
    'task_52_v1': task_52_v1_verifier,
    'task_53_v1': task_53_v1_verifier,
    'task_54_v1': task_54_v1_verifier,
    'task_55_v1': task_55_v1_verifier,
    'task_56_v1': task_56_v1_verifier,
    'task_57_v1': task_57_v1_verifier,
    'task_58_v1': task_58_v1_verifier,
    'task_59_v1': task_59_v1_verifier,
    'task_60_v1': task_60_v1_verifier,
    'task_61_v1': task_61_v1_verifier,
    'task_62_v1': task_62_v1_verifier,
    'task_63_v1': task_63_v1_verifier,
    'task_64_v1': task_64_v1_verifier,
    'task_65_v1': task_65_v1_verifier,
    'task_66_v1': task_66_v1_verifier,
    'task_67_v1': task_67_v1_verifier,
    'task_68_v1': task_68_v1_verifier,
    'task_69_v1': task_69_v1_verifier,
    'task_70_v1': task_70_v1_verifier,
    'task_71_v1': task_71_v1_verifier,
    'task_72_v1': task_72_v1_verifier,
    'task_73_v1': task_73_v1_verifier,
    'task_74_v1': task_74_v1_verifier,
    'task_75_v1': task_75_v1_verifier,
    'task_76_v1': task_76_v1_verifier,
    'task_77_v1': task_77_v1_verifier,
    'task_78_v1': task_78_v1_verifier,
    'task_79_v1': task_79_v1_verifier,
    'task_80_v1': task_80_v1_verifier,
    'task_81_v1': task_81_v1_verifier,
    'task_82_v1': task_82_v1_verifier,
    'task_83_v1': task_83_v1_verifier,
    'task_84_v1': task_84_v1_verifier,
    'task_85_v1': task_85_v1_verifier,
    'task_86_v1': task_86_v1_verifier,
    'task_87_v1': task_87_v1_verifier,
    'task_88_v1': task_88_v1_verifier,
    'task_89_v1': task_89_v1_verifier,
    'task_90_v1': task_90_v1_verifier,
    'task_91_v1': task_91_v1_verifier,
    'task_92_v1': task_92_v1_verifier,
    'task_93_v1': task_93_v1_verifier,
    'task_94_v1': task_94_v1_verifier,
    'task_95_v1': task_95_v1_verifier,
    'task_96_v1': task_96_v1_verifier,
    'task_97_v1': task_97_v1_verifier,
    'task_98_v1': task_98_v1_verifier,
    'task_99_v1': task_99_v1_verifier,
    'task_100_v1': task_100_v1_verifier,
    'task_101_v1': task_101_v1_verifier,
    'task_102_v1': task_102_v1_verifier,
    'task_103_v1': task_103_v1_verifier,
    'task_104_v1': task_104_v1_verifier,
    'task_105_v1': task_105_v1_verifier,
}


def verify_task(traj_json: Dict, task_id: str = None) -> Tuple[int, str]:
    """Main entry point to verify a v1 task from trajectory."""
    if task_id is None:
        task_id = traj_json.get('task_id', '')

    if task_id in VERIFIERS:
        return VERIFIERS[task_id](traj_json)
    else:
        return (0, f"No verifier found for {task_id}")


def main():
    parser = argparse.ArgumentParser(description='Verify AgentWorld task completion (V1 Variant Tasks)')
    parser.add_argument('--traj_path', type=str, required=True, help='Path to trajectory JSON file')
    parser.add_argument('--task_id', type=str, default=None, help='Override task ID (e.g., task_01_v1)')
    args = parser.parse_args()

    with open(args.traj_path, 'r') as f:
        traj_json = json.load(f)

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
