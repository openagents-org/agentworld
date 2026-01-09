"""
Task 45 Success Criteria Verifier
Auto-extracted from task_verifier.py
"""

from typing import Dict, Tuple
from verifier_utils import (
    get_final_inventories,
    aggregate_item_counts,
    get_all_inventories,
    count_item_in_inventories,
    has_item_in_any_inventory,
    check_agents_alive,
    get_final_hp,
    get_final_agent_status,
    get_final_agent_hp_simple,
    count_combat_kills,
    count_attack_actions,
    count_crafted_items,
    check_crafted_items,
    count_chat_messages,
    get_agent_items_by_username,
)


def task_45_verifier(traj_json: Dict) -> Tuple[int, str]:
    """Transportation Logistics - all agents survive within 45 rounds."""
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 45

    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/45"
    return (1 if passed else 0, msg)


def task_45_verifier_v1(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 57
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/57"
    return (1 if passed else 0, msg)


def task_45_verifier_v2(traj_json: Dict) -> Tuple[int, str]:
    agent_hp = get_final_agent_hp_simple(traj_json)
    all_alive = all(hp > 0 for hp in agent_hp.values()) if agent_hp else False
    num_rounds = len(traj_json.get('rounds', []))
    within_limit = num_rounds <= 77
    passed = all_alive and within_limit
    msg = f"All alive: {all_alive}, Rounds: {num_rounds}/77"
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

    # Large-scale tasks (101-105)
    'task_101': task_101_verifier,
    'task_102': task_102_verifier,
    'task_103': task_103_verifier,
    'task_104': task_104_verifier,
    'task_105': task_105_verifier,
}

VERIFIERS_V1 = {
    'task_00': task_00_verifier_v1,
    'task_01': task_01_verifier_v1,
    'task_02': task_02_verifier_v1,
    'task_03': task_03_verifier_v1,
    'task_04': task_04_verifier_v1,
    'task_05': task_05_verifier_v1,
    'task_06': task_06_verifier_v1,
    'task_07': task_07_verifier_v1,
    'task_08': task_08_verifier_v1,
    'task_09': task_09_verifier_v1,
    'task_10': task_10_verifier_v1,
    'task_11': task_11_verifier_v1,
    'task_12': task_12_verifier_v1,
    'task_13': task_13_verifier_v1,
    'task_14': task_14_verifier_v1,
    'task_15': task_15_verifier_v1,
    'task_16': task_16_verifier_v1,
    'task_17': task_17_verifier_v1,
    'task_18': task_18_verifier_v1,
    'task_38': task_38_verifier_v1,
    'task_42': task_42_verifier_v1,
    'task_44': task_44_verifier_v1,
    'task_45': task_45_verifier_v1,
    'task_57': task_57_verifier_v1,
    'task_58': task_58_verifier_v1,
    'task_59': task_59_verifier_v1,
    'task_60': task_60_verifier_v1,
    'task_61': task_61_verifier_v1,
    'task_62': task_62_verifier_v1,
    'task_63': task_63_verifier_v1,
    'task_65': task_65_verifier_v1,
    'task_66': task_66_verifier_v1,
    'task_68': task_68_verifier_v1,
    'task_69': task_69_verifier_v1,
    'task_95': task_95_verifier_v1,
    'task_97': task_97_verifier_v1,
}

VERIFIERS_V2 = {
    'task_38': task_38_verifier_v2,
    'task_42': task_42_verifier_v2,
    'task_44': task_44_verifier_v2,
    'task_45': task_45_verifier_v2,
}


def verify(traj_json: Dict) -> Tuple[int, str]:
    """Main verification entry point for task 45."""
    return task_45_verifier(traj_json)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python task_45_success_criteria.py <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {success}")
    print(f"Message: {msg}")
