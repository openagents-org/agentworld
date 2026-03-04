#!/usr/bin/env python3
"""
Comprehensive task design analysis script.
Checks for common issues in augmented task YAML files.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

AUGMENTED_DIR = Path(__file__).parent / "v1.3_augmented"

# Known correct locations from game data
RESOURCE_LOCATIONS = {
    'ironore': {'x': 545, 'y': 495, 'name': 'Iron Rock'},
    'goldnugget': {'x': 141, 'y': 5, 'name': 'Gold Rock'},
    'coal': {'x': 230, 'y': 45, 'name': 'Coal Rock (mining mountain)'},
    'nisocore': {'x': 336, 'y': 5, 'name': 'Nisoc Rock'},
    'copperore': {'x': 230, 'y': 40, 'name': 'Copper Rock'},
    'tinore': {'x': 230, 'y': 40, 'name': 'Tin Rock'},
}

# Known boss locations (from case studies)
BOSS_LOCATIONS = {
    'mermaid': {'x': 580, 'y': 755},
    'dark wolf': {'x': 1016, 'y': 682},
    'ice knight': {'x': 712, 'y': 717},
    'ancient wizard': {'x': 163, 'y': 339},
    'dark ogre': {'x': 238, 'y': 48},
    'golden golem': {'x': 548, 'y': 232},
    'ogre guardian': {'x': 291, 'y': 644},
    'hermit crab': {'x': 224, 'y': 359},
    'skeleton': {'x': 400, 'y': 600},  # Approximate - dungeons
}

# Item ID corrections
ITEM_CORRECTIONS = {
    'goldore': 'goldnugget',
    'ironbar': 'ironbar',  # Correct
    'goldbar': 'goldbar',  # Correct
}


def parse_yaml_file(yaml_path: Path) -> Dict:
    """Parse a YAML task file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def get_agent_locations(yaml_data: Dict) -> List[Dict]:
    """Extract agent locations from YAML data."""
    agents = []
    for key in yaml_data:
        if key.startswith('agent_'):
            agent = yaml_data[key]
            loc = agent.get('location', {})
            agents.append({
                'name': agent.get('username', key),
                'x': loc.get('x', 0),
                'y': loc.get('y', 0),
                'skills': agent.get('skill_levels', {}),
                'inventory': agent.get('inventory_items', []),
            })
    return agents


def check_mining_task(yaml_data: Dict, agents: List[Dict]) -> List[str]:
    """Check if mining task has correct spawn locations."""
    issues = []
    context = yaml_data.get('relevant_game_context', '').lower()
    primary = yaml_data.get('objectives', {}).get('primary', '').lower()

    # Check for iron ore mining tasks
    if 'ironore' in context or 'iron ore' in context or 'ironore' in primary:
        for agent in agents:
            if 'mining' in str(agent.get('skills', {})) or 'miner' in agent['name'].lower():
                # Check if agent is near iron rock location
                dist = abs(agent['x'] - 545) + abs(agent['y'] - 495)
                if dist > 100:
                    issues.append(f"SPAWN: {agent['name']} at ({agent['x']}, {agent['y']}) is far from Iron Rock (545, 495)")

    # Check for gold nugget mining tasks
    if 'goldnugget' in context or 'gold nugget' in context or 'goldnugget' in primary:
        for agent in agents:
            if 'mining' in str(agent.get('skills', {})) or 'miner' in agent['name'].lower() or 'prospector' in agent['name'].lower():
                # Check if agent is near gold rock location
                dist = abs(agent['x'] - 141) + abs(agent['y'] - 5)
                if dist > 100:
                    # Check if they have pre-gathered materials
                    has_gold = any(item.get('item') == 'goldnugget' for item in agent.get('inventory', []))
                    if not has_gold:
                        issues.append(f"SPAWN: {agent['name']} at ({agent['x']}, {agent['y']}) needs goldnugget but far from Gold Rock (141, 5)")

    return issues


def check_combat_task(yaml_data: Dict, agents: List[Dict]) -> List[str]:
    """Check if combat task has correct boss locations."""
    issues = []
    context = yaml_data.get('relevant_game_context', '').lower()
    primary = yaml_data.get('objectives', {}).get('primary', '').lower()
    criteria = yaml_data.get('success_criteria', [])

    # Check for boss combat tasks
    for boss_name, boss_loc in BOSS_LOCATIONS.items():
        if boss_name in context or boss_name in primary or any(boss_name in str(c).lower() for c in criteria):
            # Find combat agents
            combat_agents = [a for a in agents if any(s in str(a.get('skills', {})).lower()
                            for s in ['strength', 'defense', 'archery', 'magic'])]

            for agent in combat_agents:
                dist = abs(agent['x'] - boss_loc['x']) + abs(agent['y'] - boss_loc['y'])
                if dist > 200:
                    issues.append(f"COMBAT: {agent['name']} at ({agent['x']}, {agent['y']}) may be far from {boss_name.title()} ({boss_loc['x']}, {boss_loc['y']})")

    return issues


def check_item_ids(yaml_data: Dict) -> List[str]:
    """Check for incorrect item IDs."""
    issues = []
    yaml_str = str(yaml_data).lower()

    # Check for common mistakes
    if 'goldore' in yaml_str and 'goldnugget' not in yaml_str:
        issues.append("ITEM_ID: Uses 'goldore' instead of 'goldnugget'")

    return issues


def check_ore_reference(yaml_data: Dict) -> List[str]:
    """Check if mining task has ORE TYPE REFERENCE."""
    issues = []
    context = yaml_data.get('relevant_game_context', '').lower()

    if 'mining' in context or 'ironore' in context or 'goldnugget' in context:
        if 'ore type reference' not in context:
            issues.append("MISSING: No ORE TYPE REFERENCE in relevant_game_context")

    return issues


def analyze_task(yaml_path: Path) -> Dict:
    """Analyze a single task file for design issues."""
    yaml_data = parse_yaml_file(yaml_path)
    agents = get_agent_locations(yaml_data)

    issues = []
    issues.extend(check_mining_task(yaml_data, agents))
    issues.extend(check_combat_task(yaml_data, agents))
    issues.extend(check_item_ids(yaml_data))
    issues.extend(check_ore_reference(yaml_data))

    return {
        'file': yaml_path.name,
        'task_name': yaml_data.get('task', {}).get('name', 'Unknown'),
        'primary': yaml_data.get('objectives', {}).get('primary', ''),
        'agents': len(agents),
        'issues': issues,
    }


def main():
    """Analyze all augmented task files."""
    yaml_files = sorted(AUGMENTED_DIR.glob("task_*.yaml"))

    print(f"Analyzing {len(yaml_files)} task files...\n")

    tasks_with_issues = []

    for yaml_path in yaml_files:
        result = analyze_task(yaml_path)
        if result['issues']:
            tasks_with_issues.append(result)

    # Print summary
    print(f"=== TASK DESIGN ANALYSIS REPORT ===\n")
    print(f"Total tasks analyzed: {len(yaml_files)}")
    print(f"Tasks with issues: {len(tasks_with_issues)}\n")

    # Group by issue type
    spawn_issues = []
    combat_issues = []
    item_issues = []
    missing_ref = []

    for task in tasks_with_issues:
        for issue in task['issues']:
            if issue.startswith('SPAWN'):
                spawn_issues.append((task['file'], issue))
            elif issue.startswith('COMBAT'):
                combat_issues.append((task['file'], issue))
            elif issue.startswith('ITEM_ID'):
                item_issues.append((task['file'], issue))
            elif issue.startswith('MISSING'):
                missing_ref.append((task['file'], issue))

    if spawn_issues:
        print(f"\n--- SPAWN LOCATION ISSUES ({len(spawn_issues)}) ---")
        for file, issue in spawn_issues[:20]:  # Show first 20
            print(f"  {file}: {issue}")
        if len(spawn_issues) > 20:
            print(f"  ... and {len(spawn_issues) - 20} more")

    if combat_issues:
        print(f"\n--- COMBAT/BOSS LOCATION ISSUES ({len(combat_issues)}) ---")
        for file, issue in combat_issues[:20]:
            print(f"  {file}: {issue}")
        if len(combat_issues) > 20:
            print(f"  ... and {len(combat_issues) - 20} more")

    if item_issues:
        print(f"\n--- ITEM ID ISSUES ({len(item_issues)}) ---")
        for file, issue in item_issues:
            print(f"  {file}: {issue}")

    if missing_ref:
        print(f"\n--- MISSING ORE TYPE REFERENCE ({len(missing_ref)}) ---")
        for file, issue in missing_ref[:10]:
            print(f"  {file}")
        if len(missing_ref) > 10:
            print(f"  ... and {len(missing_ref) - 10} more")

    print("\n=== END REPORT ===")


if __name__ == "__main__":
    main()
