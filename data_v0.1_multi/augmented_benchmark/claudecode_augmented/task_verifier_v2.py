"""
Task Verifier for AgentWorld Multi-Agent Benchmark - V2 Variant Tasks
Covers: task_00_v2 to task_105_v2

Usage:
    python task_verifier_v2.py --traj_path path/to/task_XX_v2_trajectory.json

The task ID is automatically parsed from the filename (e.g., task_10_v2_trajectory.json -> task_10_v2)
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
    match = re.search(r'task_(\d+)_v2', basename)
    if match:
        return f"task_{match.group(1)}_v2"
    return None


# =============================================================================
# V2 TASK VERIFIERS (task_00_v2 to task_105_v2)
# =============================================================================

def task_00_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Complete all three major crafting projects: staff, 10 arrows, silver ring."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    arrows = count_item_in_inventories(inventories, 'arrow')
    silverring = has_item_in_any_inventory(inventories, 'silverring')

    success = staff and arrows >= 10 and silverring
    msg = f"Staff: {staff}, Arrows: {arrows}/10, Silver ring: {silverring}"
    return (1 if success else 0, msg)


def task_01_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare wizard_agent with crafted magic staff."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    msg = f"Staff crafted: {staff}"
    return (1 if staff else 0, msg)


def task_02_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Produce a batch of 10 arrows."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    success = arrows >= 10
    msg = f"Arrows: {arrows}/10"
    return (1 if success else 0, msg)


def task_03_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a silver ring."""
    inventories = get_final_inventories(traj_json)
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    msg = f"Silver ring: {silverring}"
    return (1 if silverring else 0, msg)


def task_04_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create an axe."""
    inventories = get_final_inventories(traj_json)
    axe = has_item_in_any_inventory(inventories, 'axe')
    msg = f"Axe crafted: {axe}"
    return (1 if axe else 0, msg)


def task_05_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a beryl pendant."""
    inventories = get_final_inventories(traj_json)
    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    msg = f"Beryl pendant: {berylpendant}"
    return (1 if berylpendant else 0, msg)


def task_06_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge a heavy sword."""
    inventories = get_final_inventories(traj_json)
    heavysword = has_item_in_any_inventory(inventories, 'sword2') or has_item_in_any_inventory(inventories, 'heavysword')
    msg = f"Heavy sword: {heavysword}"
    return (1 if heavysword else 0, msg)


def task_07_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Forge a high-quality pickaxe."""
    inventories = get_final_inventories(traj_json)
    pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')
    msg = f"Pickaxe: {pickaxe}"
    return (1 if pickaxe else 0, msg)


def task_08_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create bronze bars."""
    inventories = get_final_inventories(traj_json)
    bronzebar = has_item_in_any_inventory(inventories, 'bronzebar')
    msg = f"Bronze bar: {bronzebar}"
    return (1 if bronzebar else 0, msg)


def task_09_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a topaz ring."""
    inventories = get_final_inventories(traj_json)
    topazring = has_item_in_any_inventory(inventories, 'topazring')
    msg = f"Topaz ring: {topazring}"
    return (1 if topazring else 0, msg)


def task_10_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare a delicious stew."""
    inventories = get_final_inventories(traj_json)
    stew = has_item_in_any_inventory(inventories, 'stew') or has_item_in_any_inventory(inventories, 'stew2')
    msg = f"Stew: {stew}"
    return (1 if stew else 0, msg)


def task_11_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create a lightning staff (different from v1 which creates fire staff)."""
    inventories = get_final_inventories(traj_json)
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    msg = f"Lightning staff: {lightningstaff}"
    return (1 if lightningstaff else 0, msg)


def task_12_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create TWO gold rings (v1 only needs 1)."""
    inventories = get_final_inventories(traj_json)
    goldring = count_item_in_inventories(inventories, 'goldring')
    success = goldring >= 2
    msg = f"Gold rings: {goldring}/2"
    return (1 if success else 0, msg)


def task_13_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create TWO utility buckets (v1 only needs 1)."""
    inventories = get_final_inventories(traj_json)
    bucket = count_item_in_inventories(inventories, 'bucket')
    success = bucket >= 2
    msg = f"Buckets: {bucket}/2"
    return (1 if success else 0, msg)


def task_14_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Prepare 8 cooked shrimp (v1 only needs 1)."""
    inventories = get_final_inventories(traj_json)
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    success = cookedshrimp >= 8
    msg = f"Cooked shrimp: {cookedshrimp}/8"
    return (1 if success else 0, msg)


def task_15_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create TWO jellyfish smoothies (v1 only needs 1)."""
    inventories = get_final_inventories(traj_json)
    smoothie = count_item_in_inventories(inventories, 'jellyfishsmoothie')
    success = smoothie >= 2
    msg = f"Jellyfish smoothies: {smoothie}/2"
    return (1 if success else 0, msg)


def task_16_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Protect collectors while gathering 8x logs and 5x blueberry (v1: 3 logs, 2 blueberry)."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_all_agents_alive(traj_json)

    success = logs >= 8 and blueberry >= 5 and alive
    msg = f"Logs: {logs}/8, Blueberry: {blueberry}/5, All alive: {alive}"
    return (1 if success else 0, msg)


def task_17_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 5x logs and 4x blueberry (v1: 3 palmlogs, 3 peach - different items!)."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    blueberry = count_item_in_inventories(inventories, 'blueberry')

    success = logs >= 5 and blueberry >= 4
    msg = f"Logs: {logs}/5, Blueberry: {blueberry}/4"
    return (1 if success else 0, msg)


def task_18_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 8x rawshrimp and 4x icelogs (v1: 4 rawshrimp, 2 icelogs)."""
    inventories = get_final_inventories(traj_json)
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    icelogs = count_item_in_inventories(inventories, 'icelogs')

    success = rawshrimp >= 8 and icelogs >= 4
    msg = f"Rawshrimp: {rawshrimp}/8, Icelogs: {icelogs}/4"
    return (1 if success else 0, msg)


def task_19_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 6x apple and 5x wheat (v1: 4 corn, 2 tomato - different items!)."""
    inventories = get_final_inventories(traj_json)
    apple = count_item_in_inventories(inventories, 'apple')
    wheat = count_item_in_inventories(inventories, 'wheat')

    success = apple >= 6 and wheat >= 5
    msg = f"Apple: {apple}/6, Wheat: {wheat}/5"
    return (1 if success else 0, msg)


def task_20_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 8x blueberry and 5x rawtuna (v1: 4 blueberry, 3 peach - different items!)."""
    inventories = get_final_inventories(traj_json)
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    rawtuna = count_item_in_inventories(inventories, 'rawtuna')

    success = blueberry >= 8 and rawtuna >= 5
    msg = f"Blueberry: {blueberry}/8, Rawtuna: {rawtuna}/5"
    return (1 if success else 0, msg)


def task_21_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft TWO golden rings (v1: only 1)."""
    inventories = get_final_inventories(traj_json)
    goldring = count_item_in_inventories(inventories, 'goldring')
    success = goldring >= 2
    msg = f"Gold rings: {goldring}/2"
    return (1 if success else 0, msg)


def task_22_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft a Fire Staff and defeat a Frost Elemental (v1: just defeat Ice Wizard)."""
    inventories = get_final_inventories(traj_json)
    firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    alive = check_all_agents_alive(traj_json)

    success = firestaff and alive
    msg = f"Fire staff: {firestaff}, All alive: {alive}"
    return (1 if success else 0, msg)


def task_23_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest 8x jellyfish and 6x clam, craft 2x jellyfishsmoothie (v1: 4 jellyfish, 3 clam)."""
    inventories = get_final_inventories(traj_json)
    jellyfish = count_item_in_inventories(inventories, 'jellyfish')
    clam = count_item_in_inventories(inventories, 'clam')
    smoothie = count_item_in_inventories(inventories, 'jellyfishsmoothie')

    success = jellyfish >= 8 and clam >= 6 and smoothie >= 2
    msg = f"Jellyfish: {jellyfish}/8, Clam: {clam}/6, Smoothie: {smoothie}/2"
    return (1 if success else 0, msg)


def task_24_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat Golden Golem and Big Baby Spooder (v1: only Golden Golem)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_25_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat one Ice Guardian and harvest 6x Ice Oak logs (v1: just 4 ice logs)."""
    inventories = get_final_inventories(traj_json)
    ice_logs = count_item_in_inventories(inventories, 'icelogs') + \
               count_item_in_inventories(inventories, 'iceoaklogs')
    alive = check_all_agents_alive(traj_json)

    success = ice_logs >= 6 and alive
    msg = f"Ice logs: {ice_logs}/6, All alive: {alive}"
    return (1 if success else 0, msg)


def task_26_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Establish trading operations, defeat desert creatures, gather resources."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_27_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest volcanic materials and craft a fire-enchanted sword (v1: just 4 volcanic ore)."""
    inventories = get_final_inventories(traj_json)
    firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    heavysword = has_item_in_any_inventory(inventories, 'sword2') or has_item_in_any_inventory(inventories, 'heavysword')
    alive = check_all_agents_alive(traj_json)

    success = (firestaff or heavysword) and alive
    msg = f"Fire sword/staff: {firestaff or heavysword}, All alive: {alive}"
    return (1 if success else 0, msg)


def task_28_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat Dark Wolf and harvest 5x shadow wood (v1: just defeat Dark Wolf)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_29_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat Ice Knight commander (v1: just reconnaissance)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_30_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat Mermaid (55) AND Ice Knight (62) (v1: only Mermaid)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_31_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Harvest wood and craft 20x arrows (v1: 4 logs, 8 sticks)."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    success = arrows >= 20
    msg = f"Arrows: {arrows}/20"
    return (1 if success else 0, msg)


def task_32_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Explore wilderness and gather 6x blueberry and 4x apple (v1: defeat 3 Worker Ants)."""
    inventories = get_final_inventories(traj_json)
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    apple = count_item_in_inventories(inventories, 'apple')

    success = blueberry >= 6 and apple >= 4
    msg = f"Blueberry: {blueberry}/6, Apple: {apple}/4"
    return (1 if success else 0, msg)


def task_33_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mine 4x coal and 3x iron ore (v1: gather 6x logs - different objective!)."""
    inventories = get_final_inventories(traj_json)
    coal = count_item_in_inventories(inventories, 'coal')
    ironore = count_item_in_inventories(inventories, 'ironore')

    success = coal >= 4 and ironore >= 3
    msg = f"Coal: {coal}/4, Iron ore: {ironore}/3"
    return (1 if success else 0, msg)


def task_34_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft a fire staff (v1: gather 3 beryl, 4 logs - different objective!)."""
    inventories = get_final_inventories(traj_json)
    firestaff = has_item_in_any_inventory(inventories, 'firestaff')
    msg = f"Fire staff: {firestaff}"
    return (1 if firestaff else 0, msg)


def task_35_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 1 Wolf (Level 55) (v1: defeat 2 Worker Ants - different enemy!)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_36_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 2 Wolves (Level 55) (v1: defeat 5 Worker Ants - different enemy!)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_37_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 4x logs and cook 3x shrimp (v1: 5 apple, 3 blueberry - different objective!)."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')

    success = logs >= 4 and cookedshrimp >= 3
    msg = f"Logs: {logs}/4, Cooked shrimp: {cookedshrimp}/3"
    return (1 if success else 0, msg)


def task_38_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 16x sticks and 12x arrows (v1: gather 5 logs, 3 coal - different objective!)."""
    inventories = get_final_inventories(traj_json)
    sticks = count_item_in_inventories(inventories, 'stick')
    arrows = count_item_in_inventories(inventories, 'arrow')

    success = sticks >= 16 and arrows >= 12
    msg = f"Sticks: {sticks}/16, Arrows: {arrows}/12"
    return (1 if success else 0, msg)


def task_39_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Catch raw tuna and cook 4x cooked tuna (v1: 4 corn, 3 apple - different objective!)."""
    inventories = get_final_inventories(traj_json)
    cookedtuna = count_item_in_inventories(inventories, 'cookedtuna')
    success = cookedtuna >= 4
    msg = f"Cooked tuna: {cookedtuna}/4"
    return (1 if success else 0, msg)


def task_40_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 6x blueberry as healing supplies (v1: just maintain health)."""
    inventories = get_final_inventories(traj_json)
    blueberry = count_item_in_inventories(inventories, 'blueberry')
    alive = check_all_agents_alive(traj_json)

    success = blueberry >= 6 and alive
    msg = f"Blueberry: {blueberry}/6, All alive: {alive}"
    return (1 if success else 0, msg)


def task_41_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 1x pickaxe and 1x axe (v1: gather 6 logs, 4 coal - different objective!)."""
    inventories = get_final_inventories(traj_json)
    pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')
    axe = has_item_in_any_inventory(inventories, 'axe')

    success = pickaxe and axe
    msg = f"Pickaxe: {pickaxe}, Axe: {axe}"
    return (1 if success else 0, msg)


def task_42_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 4 Worker Ants (v1: practice foraging - different objective!)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_43_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 4x logs, 3x rawshrimp, 4x blueberry (v1: 6 apple, 4 blueberry - different items!)."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')
    blueberry = count_item_in_inventories(inventories, 'blueberry')

    success = logs >= 4 and rawshrimp >= 3 and blueberry >= 4
    msg = f"Logs: {logs}/4, Rawshrimp: {rawshrimp}/3, Blueberry: {blueberry}/4"
    return (1 if success else 0, msg)


def task_44_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Produce 16x sticks and 12x arrows (v1: 4 logs, 4 coal - different objective!)."""
    inventories = get_final_inventories(traj_json)
    sticks = count_item_in_inventories(inventories, 'stick')
    arrows = count_item_in_inventories(inventories, 'arrow')

    success = sticks >= 16 and arrows >= 12
    msg = f"Sticks: {sticks}/16, Arrows: {arrows}/12"
    return (1 if success else 0, msg)


def task_45_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Distribute 4x logs and 4x rawshrimp across three agents (v1: 3 logs, 3 coal)."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    rawshrimp = count_item_in_inventories(inventories, 'rawshrimp')

    success = logs >= 4 and rawshrimp >= 4
    msg = f"Logs: {logs}/4, Rawshrimp: {rawshrimp}/4"
    return (1 if success else 0, msg)


def task_46_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Mine ore and coal, smelt bars, craft 1x pickaxe (v1: smelt 6 iron bars)."""
    inventories = get_final_inventories(traj_json)
    pickaxe = has_item_in_any_inventory(inventories, 'pickaxe')
    msg = f"Pickaxe: {pickaxe}"
    return (1 if pickaxe else 0, msg)


def task_47_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create 1x base staff and upgrade to 1x lightning staff (v1: just 1 magic staff)."""
    inventories = get_final_inventories(traj_json)
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    msg = f"Lightning staff: {lightningstaff}"
    return (1 if lightningstaff else 0, msg)


def task_48_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 1x magic staff (forest) and 1x axe (mountain) (v1: 6 logs + 1 staff)."""
    inventories = get_final_inventories(traj_json)
    staff = has_item_in_any_inventory(inventories, 'staff')
    axe = has_item_in_any_inventory(inventories, 'axe')

    success = staff and axe
    msg = f"Staff: {staff}, Axe: {axe}"
    return (1 if success else 0, msg)


def task_49_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 1x silver ring and 1x emerald ring (v1: 2 silver rings)."""
    inventories = get_final_inventories(traj_json)
    silverring = has_item_in_any_inventory(inventories, 'silverring')
    emeraldring = has_item_in_any_inventory(inventories, 'emeraldring') or has_item_in_any_inventory(inventories, 'ring1')

    success = silverring and emeraldring
    msg = f"Silver ring: {silverring}, Emerald ring: {emeraldring}"
    return (1 if success else 0, msg)


def task_50_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Six warriors defeat five enemies (v1: five warriors defeat three enemies)."""
    agent_hp = get_final_agent_hp(traj_json)
    survivors = sum(1 for hp in agent_hp.values() if hp > 0)
    total = len(agent_hp) if agent_hp else 6
    success = survivors >= 5
    msg = f"Survivors: {survivors}/{total}"
    return (1 if success else 0, msg)


def task_51_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Extended survival with boss battle over 55 rounds (v1: 40 rounds, no boss)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_52_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Six-smith metalworking producing complete equipment sets (v1: four-smith)."""
    inventories = get_final_inventories(traj_json)
    weapons = ['sword1', 'sword2', 'heavysword', 'axe', 'pickaxe']
    weapon_count = sum(count_item_in_inventories(inventories, w) for w in weapons)
    success = weapon_count >= 6
    msg = f"Weapons/tools: {weapon_count}/6"
    return (1 if success else 0, msg)


def task_53_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Comprehensive culinary expedition producing multiple advanced food items."""
    inventories = get_final_inventories(traj_json)
    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'cookedtuna', 'stew', 'stew2', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    success = food_count >= 10
    msg = f"Cooked food: {food_count}/10"
    return (1 if success else 0, msg)


def task_54_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Gather 25+ logs, craft 60+ arrows, produce 5+ bows (v1: 30 logs, 80 arrows, 6 bows)."""
    inventories = get_final_inventories(traj_json)
    logs = count_item_in_inventories(inventories, 'logs')
    arrows = count_item_in_inventories(inventories, 'arrow')
    bows = count_item_in_inventories(inventories, 'woodenbow') + count_item_in_inventories(inventories, 'bow')

    success = logs >= 25 and arrows >= 60 and bows >= 5
    msg = f"Logs: {logs}/25, Arrows: {arrows}/60, Bows: {bows}/5"
    return (1 if success else 0, msg)


def task_55_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """6-phase boss raid with 4 boss battles over 55 rounds (v1: 5-phase, 3 bosses, 40 rounds)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_56_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 4x Golden Rings, 3x Lightning Staffs, 2x Heavy Swords (v1: 2, 1, 1)."""
    inventories = get_final_inventories(traj_json)
    goldring = count_item_in_inventories(inventories, 'goldring')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')

    success = goldring >= 4 and lightningstaff >= 3 and heavysword >= 2
    msg = f"Gold Rings: {goldring}/4, Lightning Staffs: {lightningstaff}/3, Heavy Swords: {heavysword}/2"
    return (1 if success else 0, msg)


def task_57_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Create 3x Ruby Rings, 3x Emerald Pendants, 2x Topaz Rings, 3x Beryl Pendants (v1: less)."""
    inventories = get_final_inventories(traj_json)
    rubyring = count_item_in_inventories(inventories, 'rubyring')
    emeraldpendant = count_item_in_inventories(inventories, 'emeraldpendant')
    topazring = count_item_in_inventories(inventories, 'topazring')
    berylpendant = count_item_in_inventories(inventories, 'berylpendant')

    success = rubyring >= 3 and emeraldpendant >= 3 and topazring >= 2 and berylpendant >= 3
    msg = f"Ruby: {rubyring}/3, Emerald: {emeraldpendant}/3, Topaz: {topazring}/2, Beryl: {berylpendant}/3"
    return (1 if success else 0, msg)


def task_58_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """7x cooked dishes, 4x decorative jewelry, 3x tools, 70+ gathered resources (v1: 3, 2, 30)."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'cookedtuna', 'stew', 'stew2', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    jewelry = ['silverring', 'goldring', 'berylpendant', 'emeraldpendant', 'topazring']
    jewelry_count = sum(count_item_in_inventories(inventories, j) for j in jewelry)

    tools = ['axe', 'pickaxe', 'bucket']
    tools_count = sum(count_item_in_inventories(inventories, t) for t in tools)

    success = food_count >= 7 and jewelry_count >= 4 and tools_count >= 3
    msg = f"Food: {food_count}/7, Jewelry: {jewelry_count}/4, Tools: {tools_count}/3"
    return (1 if success else 0, msg)


def task_59_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """9-member guild crafting 5x Golden items, 4x Staffs, 3x Specialty weapons (v1: 5-member, 2, 2, 1)."""
    inventories = get_final_inventories(traj_json)

    golden = ['goldensword', 'goldenbow', 'goldring']
    golden_count = sum(count_item_in_inventories(inventories, g) for g in golden)

    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(count_item_in_inventories(inventories, s) for s in staffs)

    weapons = ['heavysword', 'sword2', 'pickaxe']
    weapon_count = sum(count_item_in_inventories(inventories, w) for w in weapons)

    success = golden_count >= 5 and staff_count >= 4 and weapon_count >= 3
    msg = f"Golden items: {golden_count}/5, Staffs: {staff_count}/4, Weapons: {weapon_count}/3"
    return (1 if success else 0, msg)


def task_60_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Extract 120+ ores, smelt 90+ bars, craft 15+ metal items (v1: 50, 40, 6)."""
    inventories = get_final_inventories(traj_json)

    ores = count_item_in_inventories(inventories, 'ironore') + \
           count_item_in_inventories(inventories, 'goldore') + \
           count_item_in_inventories(inventories, 'coal')
    bars = count_item_in_inventories(inventories, 'ironbar') + \
           count_item_in_inventories(inventories, 'goldbar')

    items = ['pickaxe', 'axe', 'sword1', 'sword2', 'goldring', 'silverring']
    item_count = sum(count_item_in_inventories(inventories, i) for i in items)

    success = ores >= 120 and bars >= 90 and item_count >= 15
    msg = f"Ores: {ores}/120, Bars: {bars}/90, Items: {item_count}/15"
    return (1 if success else 0, msg)


def task_61_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """6+ cooked dishes, 4+ specialty items, 48+ rare ingredients (v1: 8, 4, 60)."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'cookedtuna', 'stew', 'stew2', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    success = food_count >= 6
    msg = f"Cooked dishes: {food_count}/6"
    return (1 if success else 0, msg)


def task_62_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """4 swords (including golden), 2 axes, 2 bows, 1 pickaxe = 9+ weapons (v1: 5, 3, 2, 1 = 11)."""
    inventories = get_final_inventories(traj_json)

    swords = count_item_in_inventories(inventories, 'sword1') + \
             count_item_in_inventories(inventories, 'sword2') + \
             count_item_in_inventories(inventories, 'heavysword') + \
             count_item_in_inventories(inventories, 'goldensword')
    axes = count_item_in_inventories(inventories, 'axe')
    bows = count_item_in_inventories(inventories, 'bow') + count_item_in_inventories(inventories, 'woodenbow')
    pickaxe = count_item_in_inventories(inventories, 'pickaxe')

    total = swords + axes + bows + pickaxe
    success = swords >= 4 and axes >= 2 and bows >= 2 and pickaxe >= 1 and total >= 9
    msg = f"Swords: {swords}/4, Axes: {axes}/2, Bows: {bows}/2, Pickaxe: {pickaxe}/1"
    return (1 if success else 0, msg)


def task_63_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """20+ pieces including 8 rings, 7 pendants, 5 base items (v1: 8 pieces, 3, 3, 2)."""
    inventories = get_final_inventories(traj_json)

    rings = count_item_in_inventories(inventories, 'silverring') + \
            count_item_in_inventories(inventories, 'goldring') + \
            count_item_in_inventories(inventories, 'topazring') + \
            count_item_in_inventories(inventories, 'rubyring')
    pendants = count_item_in_inventories(inventories, 'berylpendant') + \
               count_item_in_inventories(inventories, 'emeraldpendant') + \
               count_item_in_inventories(inventories, 'rubypendant')

    total = rings + pendants
    success = rings >= 8 and pendants >= 7 and total >= 20
    msg = f"Rings: {rings}/8, Pendants: {pendants}/7, Total: {total}/20"
    return (1 if success else 0, msg)


def task_64_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """80+ ice materials, 25+ ice creatures, defeat Ice Guardian boss, 12+ items (v1: 30, 8, -, 5)."""
    inventories = get_final_inventories(traj_json)

    ice_items = ['icelogs', 'iceoaklogs']
    ice_count = sum(count_item_in_inventories(inventories, i) for i in ice_items)
    alive = check_all_agents_alive(traj_json)

    success = ice_count >= 80 and alive
    msg = f"Ice materials: {ice_count}/80, All alive: {alive}"
    return (1 if success else 0, msg)


def task_65_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """15+ different consumables (v1: 6+)."""
    inventories = get_final_inventories(traj_json)

    consumables = ['healthpotion', 'manapotion', 'jellyfishsmoothie', 'cookedshrimp', 'cookedchicken',
                   'cookedbeef', 'cookedtuna', 'stew', 'stew2']
    consumable_count = sum(count_item_in_inventories(inventories, c) for c in consumables)

    success = consumable_count >= 15
    msg = f"Consumables: {consumable_count}/15"
    return (1 if success else 0, msg)


def task_66_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """80+ arrows, 8+ bows including golden bows (v1: 30+ arrows, 3+ bows)."""
    inventories = get_final_inventories(traj_json)
    arrows = count_item_in_inventories(inventories, 'arrow')
    bows = count_item_in_inventories(inventories, 'bow') + \
           count_item_in_inventories(inventories, 'woodenbow') + \
           count_item_in_inventories(inventories, 'goldenbow')

    success = arrows >= 80 and bows >= 8
    msg = f"Arrows: {arrows}/80, Bows: {bows}/8"
    return (1 if success else 0, msg)


def task_67_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Visit 6 biomes, gather 120+ resources, craft 18+ specialty items (v1: 4, 50, 8)."""
    inventories = get_final_inventories(traj_json)

    resources = ['logs', 'coal', 'ironore', 'goldore', 'rawshrimp', 'jellyfish', 'blueberry', 'corn', 'icelogs']
    resource_count = sum(count_item_in_inventories(inventories, r) for r in resources)

    crafted = ['ironbar', 'goldbar', 'cookedshrimp', 'arrow', 'sword1', 'axe', 'pickaxe', 'silverring', 'goldring']
    crafted_count = sum(count_item_in_inventories(inventories, c) for c in crafted)

    success = resource_count >= 120 and crafted_count >= 18
    msg = f"Resources: {resource_count}/120, Crafted: {crafted_count}/18"
    return (1 if success else 0, msg)


def task_68_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """12+ pickaxes, 12+ axes, 8+ buckets, 8+ specialty = 40+ total (v1: 4, 4, 3 = 15)."""
    inventories = get_final_inventories(traj_json)
    pickaxes = count_item_in_inventories(inventories, 'pickaxe')
    axes = count_item_in_inventories(inventories, 'axe')
    buckets = count_item_in_inventories(inventories, 'bucket')

    total = pickaxes + axes + buckets
    success = pickaxes >= 12 and axes >= 12 and buckets >= 8 and total >= 40
    msg = f"Pickaxes: {pickaxes}/12, Axes: {axes}/12, Buckets: {buckets}/8"
    return (1 if success else 0, msg)


def task_69_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """7+ golden items, 6+ magical staffs, 8+ elite weapons = 21+ total (v1: 3, -, 4)."""
    inventories = get_final_inventories(traj_json)

    golden = count_item_in_inventories(inventories, 'goldensword') + \
             count_item_in_inventories(inventories, 'goldenbow') + \
             count_item_in_inventories(inventories, 'goldring')
    staffs = count_item_in_inventories(inventories, 'lightningstaff') + \
             count_item_in_inventories(inventories, 'firestaff') + \
             count_item_in_inventories(inventories, 'icestaff') + \
             count_item_in_inventories(inventories, 'naturestaff')
    elite = count_item_in_inventories(inventories, 'heavysword') + \
            count_item_in_inventories(inventories, 'sword2')

    total = golden + staffs + elite
    success = golden >= 7 and staffs >= 6 and elite >= 8 and total >= 21
    msg = f"Golden: {golden}/7, Staffs: {staffs}/6, Elite: {elite}/8"
    return (1 if success else 0, msg)


def task_70_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """8-phase dungeon campaign over 65 rounds (v1: 4-phase, 40 rounds)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_71_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """6-region supply empire over 65 rounds (v1: 3-region, 40 rounds)."""
    inventories = get_final_inventories(traj_json)
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    goldbar = count_item_in_inventories(inventories, 'goldbar')

    success = ironbar >= 40 and goldbar >= 20
    msg = f"Iron bars: {ironbar}/40, Gold bars: {goldbar}/20"
    return (1 if success else 0, msg)


def task_72_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defend against 6 waves over 65 rounds (v1: 2 waves, 38 rounds)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_73_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """4-phase elemental mastery over 54 rounds (v1: 5-phase, 60 rounds)."""
    alive = check_all_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    staffs = ['lightningstaff', 'firestaff', 'icestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))

    success = alive and staff_count >= 3
    msg = f"All alive: {alive}, Elemental staffs: {staff_count}/3"
    return (1 if success else 0, msg)


def task_74_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Guild headquarters over 50 rounds (v1: 60 rounds)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_75_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deliver to three coastal refugee sites over 60-62 rounds (v1: one site, 36-38 rounds)."""
    inventories = get_final_inventories(traj_json)
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    arrow = count_item_in_inventories(inventories, 'arrow')
    alive = check_all_agents_alive(traj_json)

    success = ironbar >= 40 and cookedshrimp >= 40 and arrow >= 80 and alive
    msg = f"Iron bars: {ironbar}/40, Shrimp: {cookedshrimp}/40, Arrows: {arrow}/80, Alive: {alive}"
    return (1 if success else 0, msg)


def task_76_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Stabilize 4 conduits (Ice, Stone, Tidal, Desert) (v1: only 2 - Ice, Stone)."""
    alive = check_all_agents_alive(traj_json)
    inventories = get_final_inventories(traj_json)

    staffs = ['firestaff', 'lightningstaff', 'icestaff', 'naturestaff']
    staff_count = sum(1 for s in staffs if has_item_in_any_inventory(inventories, s))

    success = alive and staff_count >= 4
    msg = f"Alive: {alive}, Staffs: {staff_count}/4"
    return (1 if success else 0, msg)


def task_77_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Six ballista towers, survive three waves (v1: two towers, one assault)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_78_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """12 agents, 8 regions, 8 cross-regional items (v1: 6 agents, 3 regions, 3 items)."""
    inventories = get_final_inventories(traj_json)

    crafted = ['goldenbow', 'berylpendant', 'goldring', 'silverring', 'staff', 'lightningstaff', 'firestaff', 'heavysword']
    crafted_count = sum(1 for c in crafted if has_item_in_any_inventory(inventories, c))

    success = crafted_count >= 8
    msg = f"Cross-regional items: {crafted_count}/8"
    return (1 if success else 0, msg)


def task_79_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """12 agents, 7 biomes, 6-7 bosses, two dragons (v1: 6 agents, 3 biomes, 2-3 bosses, 1 dragon)."""
    agent_hp = get_final_agent_hp(traj_json)
    survivors = sum(1 for hp in agent_hp.values() if hp > 0)
    total = len(agent_hp) if agent_hp else 12
    success = survivors >= total * 0.75
    msg = f"Survivors: {survivors}/{total}"
    return (1 if success else 0, msg)


def task_80_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """12 agents prepare ultimate festival (v1: 6 agents)."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedchicken', 'cookedtuna', 'stew', 'jellyfishsmoothie']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    rings = count_item_in_inventories(inventories, 'silverring') + count_item_in_inventories(inventories, 'goldring')

    success = food_count >= 15 and rings >= 6
    msg = f"Food: {food_count}/15, Rings: {rings}/6"
    return (1 if success else 0, msg)


def task_81_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Activate pylons at 4 locations within 65 rounds (v1: 2 locations, 40 rounds)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_82_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Evacuate four civilian groups (v1: two groups)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_83_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deliver 6 cores (Earth, Flame, Tide, Gale, Ice, Shadow) (v1: only 2 - Earth, Flame)."""
    inventories = get_final_inventories(traj_json)

    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    goldring = has_item_in_any_inventory(inventories, 'goldring')
    cookedtuna = has_item_in_any_inventory(inventories, 'cookedtuna')
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')
    icestaff = has_item_in_any_inventory(inventories, 'icestaff')
    firestaff = has_item_in_any_inventory(inventories, 'firestaff')

    cores = sum([berylpendant, goldring, cookedtuna, lightningstaff, icestaff, firestaff])
    success = cores >= 6
    msg = f"Cores: {cores}/6 (beryl:{berylpendant}, gold:{goldring}, tuna:{cookedtuna}, lightning:{lightningstaff}, ice:{icestaff}, fire:{firestaff})"
    return (1 if success else 0, msg)


def task_84_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Reconnect 4 points and escort carts along all routes (v1: 2 points, 1 cart)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_85_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Deliver 30 icelogs, 20 iron bars, 3 lightningstaff, 3 icestaff (v1: fewer items)."""
    inventories = get_final_inventories(traj_json)

    icelogs = count_item_in_inventories(inventories, 'icelogs')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    icestaff = count_item_in_inventories(inventories, 'icestaff')
    alive = check_all_agents_alive(traj_json)

    success = icelogs >= 30 and ironbar >= 20 and lightningstaff >= 3 and icestaff >= 3 and alive
    msg = f"Ice logs: {icelogs}/30, Iron: {ironbar}/20, Lightning: {lightningstaff}/3, Ice staff: {icestaff}/3"
    return (1 if success else 0, msg)


def task_86_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """3 heavy swords, 2 golden bows, 2 lightningstaff, 1 firestaff (v1: same except 1 lightningstaff)."""
    inventories = get_final_inventories(traj_json)

    heavysword = count_item_in_inventories(inventories, 'heavysword') + count_item_in_inventories(inventories, 'sword2')
    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')

    success = heavysword >= 3 and goldenbow >= 2 and lightningstaff >= 2 and firestaff >= 1
    msg = f"Heavy swords: {heavysword}/3, Golden bows: {goldenbow}/2, Lightning: {lightningstaff}/2, Fire: {firestaff}/1"
    return (1 if success else 0, msg)


def task_87_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Clear three silt chokepoints (v1: two)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_88_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat Water Guardian and Ogre Guardian (same as v1 but order reversed)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_89_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 4 relics (Beryl Pendant, Ruby Pendant, Emerald Ring, Lightning Staff) before Round 60 (v1: 3 relics, Round 50)."""
    inventories = get_final_inventories(traj_json)

    berylpendant = has_item_in_any_inventory(inventories, 'berylpendant')
    rubypendant = has_item_in_any_inventory(inventories, 'rubypendant')
    emeraldring = has_item_in_any_inventory(inventories, 'emeraldring')
    lightningstaff = has_item_in_any_inventory(inventories, 'lightningstaff')

    relics = sum([berylpendant, rubypendant, emeraldring, lightningstaff])
    success = relics >= 4
    msg = f"Beryl: {berylpendant}, Ruby: {rubypendant}, Emerald: {emeraldring}, Lightning: {lightningstaff}"
    return (1 if success else 0, msg)


def task_90_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """4 goldbar pylons, 2 lightningstaff, 1 firestaff, 2 rings at 3 towers (v1: 3 pylons, 1 lightningstaff, 2 towers)."""
    inventories = get_final_inventories(traj_json)

    goldbar = count_item_in_inventories(inventories, 'goldbar')
    lightningstaff = count_item_in_inventories(inventories, 'lightningstaff')
    firestaff = count_item_in_inventories(inventories, 'firestaff')
    rings = count_item_in_inventories(inventories, 'goldring') + count_item_in_inventories(inventories, 'silverring')
    alive = check_all_agents_alive(traj_json)

    success = goldbar >= 4 and lightningstaff >= 2 and firestaff >= 1 and rings >= 2 and alive
    msg = f"Gold bars: {goldbar}/4, Lightning: {lightningstaff}/2, Fire: {firestaff}/1, Rings: {rings}/2, Alive: {alive}"
    return (1 if success else 0, msg)


def task_91_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Defeat 2+ bosses, craft 4+ equipment, prepare 18+ food items (v1: 15+ food)."""
    inventories = get_final_inventories(traj_json)

    equipment = ['heavysword', 'goldring', 'icestaff', 'silverring', 'axe', 'emeraldpendant']
    equipment_count = sum(1 for e in equipment if has_item_in_any_inventory(inventories, e))

    food = ['cookedshrimp', 'cookedchicken', 'cookedbeef', 'cookedtuna', 'jellyfishsmoothie', 'stew']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    alive = check_all_agents_alive(traj_json)
    success = alive and equipment_count >= 4 and food_count >= 18
    msg = f"Alive: {alive}, Equipment: {equipment_count}/4, Food: {food_count}/18"
    return (1 if success else 0, msg)


def task_92_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Continental trade network over 55 rounds (v1: 45 rounds)."""
    inventories = get_final_inventories(traj_json)

    cookedshrimp = count_item_in_inventories(inventories, 'cookedshrimp')
    ironbar = count_item_in_inventories(inventories, 'ironbar')
    goldbar = count_item_in_inventories(inventories, 'goldbar')

    success = cookedshrimp >= 25 and ironbar >= 15 and goldbar >= 8
    msg = f"Shrimp: {cookedshrimp}/25, Iron: {ironbar}/15, Gold: {goldbar}/8"
    return (1 if success else 0, msg)


def task_93_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Fortress defense over 60 rounds (v1: 50 rounds)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_94_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """3 fishing fleets, 45+ trade goods (v1: 40+ trade goods)."""
    inventories = get_final_inventories(traj_json)

    seafood = ['rawshrimp', 'jellyfish', 'cookedshrimp', 'rawtuna']
    trade_goods = ['arrow', 'sword1', 'axe', 'pickaxe', 'goldring', 'silverring']

    seafood_count = sum(count_item_in_inventories(inventories, s) for s in seafood)
    trade_count = sum(count_item_in_inventories(inventories, t) for t in trade_goods)
    total = seafood_count + trade_count

    success = total >= 45
    msg = f"Seafood: {seafood_count}, Trade goods: {trade_count}, Total: {total}/45"
    return (1 if success else 0, msg)


def task_95_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """180+ seafood items, 3+ sea bosses (v1: 80+ seafood, 2+ bosses)."""
    inventories = get_final_inventories(traj_json)

    seafood = ['rawshrimp', 'jellyfish', 'cookedshrimp', 'rawtuna', 'clam', 'cookedtuna']
    seafood_count = sum(count_item_in_inventories(inventories, s) for s in seafood)

    success = seafood_count >= 180
    msg = f"Seafood: {seafood_count}/180"
    return (1 if success else 0, msg)


def task_96_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """4 regions, 120+ supplies, 4 rescue camps (v1: 2 regions, 60+ supplies, 2 camps)."""
    inventories = get_final_inventories(traj_json)

    supplies = ['flask', 'apple', 'cookedshrimp', 'logs', 'pickaxe']
    supply_count = sum(count_item_in_inventories(inventories, s) for s in supplies)
    alive = check_all_agents_alive(traj_json)

    success = supply_count >= 120 and alive
    msg = f"Supplies: {supply_count}/120, All alive: {alive}"
    return (1 if success else 0, msg)


def task_97_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """150+ food items (v1: 80+ food items)."""
    inventories = get_final_inventories(traj_json)

    food = ['corn', 'tomato', 'blueberry', 'apple', 'cookedshrimp', 'cookedchicken', 'cookedbeef', 'rawshrimp', 'cookedtuna']
    food_count = sum(count_item_in_inventories(inventories, f) for f in food)

    success = food_count >= 150
    msg = f"Food items: {food_count}/150"
    return (1 if success else 0, msg)


def task_98_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """4 mine sites, 100+ bars, 30+ finished products (v1: 2 sites, 50+ bars, 10+ products)."""
    inventories = get_final_inventories(traj_json)

    bars = count_item_in_inventories(inventories, 'ironbar') + count_item_in_inventories(inventories, 'goldbar')

    products = ['heavysword', 'axe', 'goldring', 'silverring', 'pickaxe', 'sword1', 'sword2']
    product_count = sum(count_item_in_inventories(inventories, p) for p in products)

    success = bars >= 100 and product_count >= 30
    msg = f"Bars: {bars}/100, Products: {product_count}/30"
    return (1 if success else 0, msg)


def task_99_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """5 exhibition arenas, 70+ prepared items (v1: 3 arenas, 35+ items)."""
    inventories = get_final_inventories(traj_json)

    food = ['cookedshrimp', 'cookedtuna', 'cookedchicken', 'jellyfishsmoothie', 'stew']
    crafted = ['heavysword', 'axe', 'goldring', 'silverring', 'berylpendant', 'lightningstaff']

    food_count = sum(count_item_in_inventories(inventories, f) for f in food)
    crafted_count = sum(count_item_in_inventories(inventories, c) for c in crafted)
    total = food_count + crafted_count

    success = total >= 70
    msg = f"Food: {food_count}, Crafted: {crafted_count}, Total: {total}/70"
    return (1 if success else 0, msg)


def task_100_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """10+ regions, 120+ documented findings, 8+ observation posts (v1: 6, 80, 4)."""
    inventories = get_final_inventories(traj_json)

    resources = ['logs', 'ironore', 'coal', 'goldore', 'blueberry', 'corn', 'rawshrimp', 'icelogs', 'jellyfish']
    total = sum(count_item_in_inventories(inventories, r) for r in resources)
    found_types = sum(1 for r in resources if count_item_in_inventories(inventories, r) > 0)
    alive = check_all_agents_alive(traj_json)

    success = total >= 120 and found_types >= 8 and alive
    msg = f"Resources: {total}/120, Types: {found_types}/8, Alive: {alive}"
    return (1 if success else 0, msg)


def task_101_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Construct Citadel Foundation (same as v1)."""
    inventories = get_final_inventories(traj_json)

    ironbar = count_item_in_inventories(inventories, 'ironbar')
    logs = count_item_in_inventories(inventories, 'logs')
    alive = check_all_agents_alive(traj_json)

    success = ironbar >= 40 and logs >= 40 and alive
    msg = f"Iron bars: {ironbar}/40, Logs: {logs}/40, Alive: {alive}"
    return (1 if success else 0, msg)


def task_102_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Craft 7 Fire Staffs, 7 Ice Staffs, 7 Nature Staffs (v1: 3 each)."""
    inventories = get_final_inventories(traj_json)

    firestaff = count_item_in_inventories(inventories, 'firestaff')
    icestaff = count_item_in_inventories(inventories, 'icestaff')
    naturestaff = count_item_in_inventories(inventories, 'naturestaff')

    success = firestaff >= 7 and icestaff >= 7 and naturestaff >= 7
    msg = f"Fire: {firestaff}/7, Ice: {icestaff}/7, Nature: {naturestaff}/7"
    return (1 if success else 0, msg)


def task_103_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Escort all 8 Settlers (same as v1)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_104_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Secure Northern and Eastern borders (same as v1)."""
    alive = check_all_agents_alive(traj_json)
    msg = f"All agents alive: {alive}"
    return (1 if alive else 0, msg)


def task_105_v2_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Produce 7 Golden Bows and 2 Golden Swords (v1: 3 bows, 1 sword)."""
    inventories = get_final_inventories(traj_json)

    goldenbow = count_item_in_inventories(inventories, 'goldenbow')
    goldensword = count_item_in_inventories(inventories, 'goldensword')
    alive = check_all_agents_alive(traj_json)

    success = goldenbow >= 7 and goldensword >= 2 and alive
    msg = f"Golden bows: {goldenbow}/7, Golden swords: {goldensword}/2, Alive: {alive}"
    return (1 if success else 0, msg)


# =============================================================================
# VERIFIER REGISTRY
# =============================================================================

VERIFIERS = {
    'task_00_v2': task_00_v2_verifier,
    'task_01_v2': task_01_v2_verifier,
    'task_02_v2': task_02_v2_verifier,
    'task_03_v2': task_03_v2_verifier,
    'task_04_v2': task_04_v2_verifier,
    'task_05_v2': task_05_v2_verifier,
    'task_06_v2': task_06_v2_verifier,
    'task_07_v2': task_07_v2_verifier,
    'task_08_v2': task_08_v2_verifier,
    'task_09_v2': task_09_v2_verifier,
    'task_10_v2': task_10_v2_verifier,
    'task_11_v2': task_11_v2_verifier,
    'task_12_v2': task_12_v2_verifier,
    'task_13_v2': task_13_v2_verifier,
    'task_14_v2': task_14_v2_verifier,
    'task_15_v2': task_15_v2_verifier,
    'task_16_v2': task_16_v2_verifier,
    'task_17_v2': task_17_v2_verifier,
    'task_18_v2': task_18_v2_verifier,
    'task_19_v2': task_19_v2_verifier,
    'task_20_v2': task_20_v2_verifier,
    'task_21_v2': task_21_v2_verifier,
    'task_22_v2': task_22_v2_verifier,
    'task_23_v2': task_23_v2_verifier,
    'task_24_v2': task_24_v2_verifier,
    'task_25_v2': task_25_v2_verifier,
    'task_26_v2': task_26_v2_verifier,
    'task_27_v2': task_27_v2_verifier,
    'task_28_v2': task_28_v2_verifier,
    'task_29_v2': task_29_v2_verifier,
    'task_30_v2': task_30_v2_verifier,
    'task_31_v2': task_31_v2_verifier,
    'task_32_v2': task_32_v2_verifier,
    'task_33_v2': task_33_v2_verifier,
    'task_34_v2': task_34_v2_verifier,
    'task_35_v2': task_35_v2_verifier,
    'task_36_v2': task_36_v2_verifier,
    'task_37_v2': task_37_v2_verifier,
    'task_38_v2': task_38_v2_verifier,
    'task_39_v2': task_39_v2_verifier,
    'task_40_v2': task_40_v2_verifier,
    'task_41_v2': task_41_v2_verifier,
    'task_42_v2': task_42_v2_verifier,
    'task_43_v2': task_43_v2_verifier,
    'task_44_v2': task_44_v2_verifier,
    'task_45_v2': task_45_v2_verifier,
    'task_46_v2': task_46_v2_verifier,
    'task_47_v2': task_47_v2_verifier,
    'task_48_v2': task_48_v2_verifier,
    'task_49_v2': task_49_v2_verifier,
    'task_50_v2': task_50_v2_verifier,
    'task_51_v2': task_51_v2_verifier,
    'task_52_v2': task_52_v2_verifier,
    'task_53_v2': task_53_v2_verifier,
    'task_54_v2': task_54_v2_verifier,
    'task_55_v2': task_55_v2_verifier,
    'task_56_v2': task_56_v2_verifier,
    'task_57_v2': task_57_v2_verifier,
    'task_58_v2': task_58_v2_verifier,
    'task_59_v2': task_59_v2_verifier,
    'task_60_v2': task_60_v2_verifier,
    'task_61_v2': task_61_v2_verifier,
    'task_62_v2': task_62_v2_verifier,
    'task_63_v2': task_63_v2_verifier,
    'task_64_v2': task_64_v2_verifier,
    'task_65_v2': task_65_v2_verifier,
    'task_66_v2': task_66_v2_verifier,
    'task_67_v2': task_67_v2_verifier,
    'task_68_v2': task_68_v2_verifier,
    'task_69_v2': task_69_v2_verifier,
    'task_70_v2': task_70_v2_verifier,
    'task_71_v2': task_71_v2_verifier,
    'task_72_v2': task_72_v2_verifier,
    'task_73_v2': task_73_v2_verifier,
    'task_74_v2': task_74_v2_verifier,
    'task_75_v2': task_75_v2_verifier,
    'task_76_v2': task_76_v2_verifier,
    'task_77_v2': task_77_v2_verifier,
    'task_78_v2': task_78_v2_verifier,
    'task_79_v2': task_79_v2_verifier,
    'task_80_v2': task_80_v2_verifier,
    'task_81_v2': task_81_v2_verifier,
    'task_82_v2': task_82_v2_verifier,
    'task_83_v2': task_83_v2_verifier,
    'task_84_v2': task_84_v2_verifier,
    'task_85_v2': task_85_v2_verifier,
    'task_86_v2': task_86_v2_verifier,
    'task_87_v2': task_87_v2_verifier,
    'task_88_v2': task_88_v2_verifier,
    'task_89_v2': task_89_v2_verifier,
    'task_90_v2': task_90_v2_verifier,
    'task_91_v2': task_91_v2_verifier,
    'task_92_v2': task_92_v2_verifier,
    'task_93_v2': task_93_v2_verifier,
    'task_94_v2': task_94_v2_verifier,
    'task_95_v2': task_95_v2_verifier,
    'task_96_v2': task_96_v2_verifier,
    'task_97_v2': task_97_v2_verifier,
    'task_98_v2': task_98_v2_verifier,
    'task_99_v2': task_99_v2_verifier,
    'task_100_v2': task_100_v2_verifier,
    'task_101_v2': task_101_v2_verifier,
    'task_102_v2': task_102_v2_verifier,
    'task_103_v2': task_103_v2_verifier,
    'task_104_v2': task_104_v2_verifier,
    'task_105_v2': task_105_v2_verifier,
}


def verify_task(traj_json: Dict, task_id: str = None) -> Tuple[int, str]:
    """Main entry point to verify a v2 task from trajectory."""
    if task_id is None:
        task_id = traj_json.get('task_id', '')

    if task_id in VERIFIERS:
        return VERIFIERS[task_id](traj_json)
    else:
        return (0, f"No verifier found for {task_id}")


def main():
    parser = argparse.ArgumentParser(description='Verify AgentWorld task completion (V2 Variant Tasks)')
    parser.add_argument('--traj_path', type=str, required=True, help='Path to trajectory JSON file')
    parser.add_argument('--task_id', type=str, default=None, help='Override task ID (e.g., task_01_v2)')
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
