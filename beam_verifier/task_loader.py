"""
Task Loader Module

Loads task YAML files and converts agent configurations to SimulationState format.
"""

import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


# Skill name to type ID mapping (from modules.ts Skills enum)
SKILL_NAME_TO_TYPE = {
    'lumberjacking': 0,
    'accuracy': 1,
    'archery': 2,
    'health': 3,
    'magic': 4,
    'mining': 5,
    'strength': 6,
    'defense': 7,
    'fishing': 8,
    'cooking': 9,
    'smithing': 10,
    'crafting': 11,
    'fletching': 12,
    'smelting': 13,
    'foraging': 14,
    'eating': 15,
    'loitering': 16,
}

# Equipment slot name to type ID mapping (from modules.ts Equipment enum)
EQUIPMENT_SLOT_TO_TYPE = {
    'armour': 0,
    'armor': 0,  # alias
    'boots': 1,
    'pendant': 2,
    'ring': 3,
    'weapon': 4,
    'arrows': 5,
    'weaponskin': 6,
    'armourskin': 7,
}

# Item key to equipment slot mapping (common items)
ITEM_TO_SLOT = {
    # Weapons
    'sword': 4, 'axe': 4, 'morningstar': 4, 'dagger': 4, 'pickaxe': 4,
    'staff': 4, 'bow': 4, 'club': 4, 'mace': 4, 'hatchet': 4,
    'hammer': 4, 'spear': 4, 'scimitar': 4, 'battleaxe': 4,
    'ironsword': 4, 'ironaxe': 4, 'ironpickaxe': 4,
    'steelsword': 4, 'steelaxe': 4, 'steelpickaxe': 4,
    'goldsword': 4, 'goldaxe': 4, 'goldpickaxe': 4,
    'lightningstaff': 4, 'firestaff': 4, 'icestaff': 4,
    # Armour
    'leatherarmor': 0, 'leatherarmour': 0, 'chainmail': 0, 'platearmor': 0,
    'ironarmor': 0, 'steelarmor': 0, 'goldarmor': 0, 'wizardrobe': 0,
    # Boots
    'leatherboots': 1, 'ironboots': 1, 'steelboots': 1, 'goldboots': 1, 'wizardboots': 1,
    # Pendants
    'silverpendant': 2, 'goldpendant': 2, 'berylpendant': 2, 'rubypendant': 2,
    # Rings
    'goldring': 3, 'silverring': 3, 'bronzering': 3, 'topazring': 3,
    'emeraldring': 3, 'sapphirering': 3, 'diamondring': 3, 'rubyring': 3,
    # Arrows
    'arrow': 5, 'ironarrow': 5, 'steelarrow': 5, 'poisonarrow': 5,
}

# Experience per level (simplified - first 100 levels)
LEVEL_EXP = [
    0, 83, 174, 276, 388, 512, 650, 801, 969, 1154,
    1358, 1584, 1833, 2107, 2411, 2746, 3115, 3523, 3973, 4470,
    5018, 5624, 6291, 7028, 7842, 8740, 9730, 10824, 12031, 13363,
    14833, 16456, 18247, 20224, 22406, 24815, 27473, 30408, 33648, 37224,
    41171, 45529, 50339, 55649, 61512, 67983, 75127, 83014, 91721, 101333,
    111945, 123660, 136594, 150872, 166636, 184040, 203254, 224466, 247886, 273742,
    302288, 333804, 368599, 407015, 449428, 496254, 547953, 605032, 668051, 737627,
    814445, 899257, 992895, 1096278, 1210421, 1336443, 1475581, 1629200, 1798808, 1986068,
    2192818, 2421087, 2673114, 2951373, 3258594, 3597792, 3972294, 4385776, 4842295, 5346332,
    5902831, 6517253, 7195629, 7944614, 8771558, 9684577, 10692629, 11805606, 13034431, 14391160
]


def level_to_experience(level: int) -> int:
    """Convert a skill level to experience points."""
    if level <= 0:
        return 0
    if level >= len(LEVEL_EXP):
        return LEVEL_EXP[-1]
    return LEVEL_EXP[level]


def get_item_slot(item_key: str) -> Optional[int]:
    """Get the equipment slot for an item, or None if not equippable."""
    key_lower = item_key.lower()
    return ITEM_TO_SLOT.get(key_lower)


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    username: str
    new_character: bool = True
    location: Dict[str, int] = field(default_factory=dict)
    skill_levels: Dict[str, int] = field(default_factory=dict)
    inventory_items: List[Dict[str, Any]] = field(default_factory=list)
    equipped_items: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TaskConfig:
    """Configuration for a complete task."""
    name: str
    description: str
    primary_objective: str
    relevant_game_context: str
    max_action_steps: int
    agents: Dict[str, AgentConfig]
    success_criteria: List[str]
    task_id: str = ""


def load_task(yaml_path: str) -> TaskConfig:
    """
    Load a task YAML file and return structured config.

    Args:
        yaml_path: Path to the YAML task file

    Returns:
        TaskConfig object with all task information
    """
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    # Extract task info
    task_info = data.get('task', {})
    objectives = data.get('objectives', {})

    # Extract task ID from filename
    import os
    filename = os.path.basename(yaml_path)
    task_id = filename.replace('.yaml', '').replace('.yml', '')

    # Parse agents
    agents = {}
    for key in data:
        if key.startswith('agent_'):
            agent_data = data[key]
            agent = AgentConfig(
                username=agent_data.get('username', ''),
                new_character=agent_data.get('new_character', True),
                location=agent_data.get('location', {}),
                skill_levels=agent_data.get('skill_levels', {}),
                inventory_items=agent_data.get('inventory_items', []),
                equipped_items=agent_data.get('equipped_items', [])
            )
            agents[agent.username] = agent

    return TaskConfig(
        name=task_info.get('name', ''),
        description=task_info.get('description', ''),
        primary_objective=objectives.get('primary', ''),
        relevant_game_context=data.get('relevant_game_context', ''),
        max_action_steps=data.get('max_action_steps', 25),
        agents=agents,
        success_criteria=data.get('success_criteria', []),
        task_id=task_id
    )


def agent_to_initial_state(agent: AgentConfig) -> Dict[str, Any]:
    """
    Convert an AgentConfig to a SimulationState dictionary.

    Args:
        agent: AgentConfig from task YAML

    Returns:
        Dictionary matching SimulationState structure
    """
    # Convert skill levels to experience
    skills = {}
    for skill_name, level in agent.skill_levels.items():
        skill_type = SKILL_NAME_TO_TYPE.get(skill_name.lower())
        if skill_type is not None:
            skills[skill_type] = level_to_experience(level)

    # Calculate HP/Mana from health/magic skills
    health_level = agent.skill_levels.get('health', 10)
    magic_level = agent.skill_levels.get('magic', 1)

    # HP = 39 + (health_level * 10), Mana = magic_level * 10
    max_hp = 39 + (health_level * 10)
    max_mana = magic_level * 10

    # Initialize inventory (25 slots, all null)
    inventory = [None] * 25

    # Add inventory items
    slot_index = 0
    for item in agent.inventory_items:
        if slot_index >= 25:
            break
        item_key = item.get('item', '')
        count = item.get('count', 1)
        if item_key:
            inventory[slot_index] = {'key': item_key, 'count': count}
            slot_index += 1

    # Initialize equipment (by slot type)
    equipment = {
        0: None,  # Armour
        1: None,  # Boots
        2: None,  # Pendant
        3: None,  # Ring
        4: None,  # Weapon
        5: None,  # Arrows
    }

    # Add equipped items
    for item in agent.equipped_items:
        item_key = item.get('item', '')
        count = item.get('count', 1)
        if item_key:
            slot = get_item_slot(item_key)
            if slot is not None:
                equipment[slot] = {'key': item_key, 'count': count}

    return {
        'x': agent.location.get('x', 0),
        'y': agent.location.get('y', 0),
        'hitPoints': max_hp,
        'maxHitPoints': max_hp,
        'mana': max_mana,
        'maxMana': max_mana,
        'level': health_level,
        'dead': False,
        'skills': skills,
        'inventory': inventory,
        'equipment': equipment,
        'poisoned': False,
        'stunned': False
    }


def task_to_initial_states(task: TaskConfig) -> Dict[str, Dict[str, Any]]:
    """
    Convert all agents in a task to initial SimulationState dictionaries.

    Args:
        task: TaskConfig from load_task()

    Returns:
        Dictionary mapping agent username to SimulationState
    """
    states = {}
    for username, agent in task.agents.items():
        states[username] = agent_to_initial_state(agent)
    return states


def get_task_context(task: TaskConfig) -> str:
    """
    Generate a context string for Claude prompts.

    Args:
        task: TaskConfig from load_task()

    Returns:
        String describing the task for Claude
    """
    context = f"""# Task: {task.name}

## Description
{task.description}

## Primary Objective
{task.primary_objective}

## Game Context
{task.relevant_game_context}

## Agents
"""
    for username, agent in task.agents.items():
        context += f"\n### {username}\n"
        context += f"- Location: ({agent.location.get('x', 0)}, {agent.location.get('y', 0)})\n"
        context += f"- Skills: {agent.skill_levels}\n"
        context += f"- Inventory: {[item.get('item') for item in agent.inventory_items]}\n"
        context += f"- Equipped: {[item.get('item') for item in agent.equipped_items]}\n"

    context += f"\n## Success Criteria\n"
    for criterion in task.success_criteria:
        context += f"- {criterion}\n"

    context += f"\n## Max Steps: {task.max_action_steps}\n"

    return context


if __name__ == '__main__':
    # Test loading
    import sys
    if len(sys.argv) > 1:
        task = load_task(sys.argv[1])
        print(f"Task: {task.name}")
        print(f"Agents: {list(task.agents.keys())}")
        states = task_to_initial_states(task)
        for name, state in states.items():
            print(f"\n{name}:")
            print(f"  Position: ({state['x']}, {state['y']})")
            print(f"  HP: {state['hitPoints']}/{state['maxHitPoints']}")
            print(f"  Skills: {state['skills']}")
