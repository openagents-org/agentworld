#!/usr/bin/env python3
"""
Generator script for augmented task verifiers.
Creates success_criteria.py files for all tasks in v1.3_augmented/.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Directory paths
SCRIPT_DIR = Path(__file__).parent
AUGMENTED_DIR = SCRIPT_DIR / "v1.3_augmented"
BENCHMARK_DIR = SCRIPT_DIR / "v1.3_benchmark"


def parse_yaml_file(yaml_path: Path) -> Dict:
    """Parse a YAML task file and return its contents."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def extract_task_info(yaml_path: Path) -> Tuple[int, str, str]:
    """Extract task number, name, and variant from filename.

    Example: task_19_farm_defense_v1.yaml -> (19, 'farm_defense', 'v1')
    """
    filename = yaml_path.stem  # e.g., task_19_farm_defense_v1

    # Pattern: task_XX_name_vN
    match = re.match(r'task_(\d+)_(.+)_(v[12])$', filename)
    if match:
        task_num = int(match.group(1))
        task_name = match.group(2)
        variant = match.group(3)
        return task_num, task_name, variant

    raise ValueError(f"Could not parse filename: {yaml_path}")


def extract_thresholds_from_criteria(criteria_list: List[str]) -> Dict:
    """Extract numeric thresholds and targets from success criteria text.

    Returns a dict with extracted info like:
    {
        'items': {'corn': 5, 'tomato': 2},
        'agent_items': {'corn_harvester': {'corn': 5}},
        'kills': {'Ogre': 2, 'Goblin': 3},
        'check_alive': True
    }
    """
    result = {
        'items': {},
        'agent_items': {},
        'kills': {},
        'check_alive': False,
        'has_items': [],  # Items that just need to exist (1+)
    }

    # Known mob names for detection (lowercase)
    mob_names = ['goblin', 'goblins', 'ogre', 'ogres', 'wolf', 'wolves', 'skeleton',
                 'skeletons', 'mermaid', 'dark wolf', 'ice knight', 'guardian',
                 'ancient wizard', 'dark ogre', 'golden golem', 'ogre guardian',
                 'hermit crab', 'dragon', 'ice wizard', 'water guardian']

    for criterion in criteria_list:
        criterion_lower = criterion.lower()

        # Check for "all agents alive" type criteria
        if 'alive' in criterion_lower or 'survive' in criterion_lower:
            result['check_alive'] = True

        # Pattern: "agent_name has at least Nx item"
        agent_item_match = re.search(
            r'(\w+_agent)\s+has\s+(?:at\s+least\s+)?(\d+)x?\s+(\w+)',
            criterion_lower
        )
        if agent_item_match:
            agent = agent_item_match.group(1)
            count = int(agent_item_match.group(2))
            item = agent_item_match.group(3)
            if agent not in result['agent_items']:
                result['agent_items'][agent] = {}
            result['agent_items'][agent][item] = count
            continue

        # Pattern: "MobName at (x, y) is defeated" - named boss at location
        boss_location_match = re.search(r'([A-Za-z][A-Za-z\s]+?)\s+at\s+\(\d+,\s*\d+\)\s+is\s+defeated', criterion)
        if boss_location_match:
            mob = boss_location_match.group(1).strip()
            if mob:
                result['kills'][mob] = result['kills'].get(mob, 0) + 1
            continue

        # Pattern: "Nx MobName are/is defeated" or "Nx MobName defeated"
        mob_defeat_match = re.search(r'(\d+)x?\s+(\w+)\s+(?:are\s+|is\s+)?defeated', criterion_lower)
        if mob_defeat_match:
            count = int(mob_defeat_match.group(1))
            mob = mob_defeat_match.group(2).capitalize()
            # Handle plural
            if mob.endswith('s') and mob.lower() not in ['boss', 'class']:
                mob = mob[:-1]
            result['kills'][mob] = result['kills'].get(mob, 0) + count
            continue

        # Pattern: "defeat Nx MobName" or "kill Nx mobs"
        kill_match = re.search(r'defeat\s+(\d+)x?\s+(\w+)', criterion_lower)
        if kill_match:
            count = int(kill_match.group(1))
            mob = kill_match.group(2).capitalize()
            # Handle plural
            if mob.endswith('s') and mob.lower() not in ['boss', 'class']:
                mob = mob[:-1]
            result['kills'][mob] = result['kills'].get(mob, 0) + count
            continue

        # Pattern: "defeat the MobName" (single named boss without location)
        boss_match = re.search(r'defeat\s+(?:the\s+)?([A-Za-z][A-Za-z\s]+?)(?:\s+and\s+|\s*$)', criterion_lower)
        if boss_match and 'defeat' in criterion_lower and 'at (' not in criterion_lower:
            mob = boss_match.group(1).strip().title()
            if mob and len(mob) > 2 and mob.lower() not in ['the', 'all', 'both']:
                result['kills'][mob] = result['kills'].get(mob, 0) + 1

        # Pattern: "Nx item" or "at least Nx item" (general inventory) - exclude mob names
        item_match = re.search(r'(?:at\s+least\s+)?(\d+)x?\s+(\w+)', criterion_lower)
        if item_match:
            count = int(item_match.group(1))
            item = item_match.group(2)
            # Skip if it's a mob name or already handled
            if item.lower() not in mob_names and 'defeat' not in criterion_lower:
                result['items'][item] = count

        # Pattern: "crafts a magic staff" - multi-word item with "a"
        craft_multiword_match = re.search(r'craft[sed]*\s+a\s+([a-z]+\s+[a-z]+)', criterion_lower)
        if craft_multiword_match:
            # Extract just the last word (e.g., "magic staff" -> "staff")
            full_item = craft_multiword_match.group(1)
            item = full_item.split()[-1]  # Get last word
            if item not in ['and', 'to', 'for'] and item not in result['has_items']:
                result['has_items'].append(item)
            continue

        # Pattern: "crafts item" single word (like "crafts sticks")
        craft_match = re.search(r'craft[sed]*\s+(?:a\s+)?(\w+)', criterion_lower)
        if craft_match:
            item = craft_match.group(1)
            # Filter out common words that aren't items
            if item not in ['a', 'the', 'an', 'and', 'to', 'for', 'it'] and item not in result['has_items']:
                result['has_items'].append(item)

        # Pattern: "equips the magic staff" - item should exist
        equip_match = re.search(r'equips?\s+(?:the\s+)?([a-z]+(?:\s+[a-z]+)?)', criterion_lower)
        if equip_match:
            full_item = equip_match.group(1)
            item = full_item.split()[-1]  # Get last word
            # Filter out common words
            if item not in ['and', 'to', 'for', 'it', 'a', 'the'] and item not in result['has_items']:
                result['has_items'].append(item)

    return result


def get_benchmark_verifier_path(task_num: int) -> Optional[Path]:
    """Get the path to the benchmark verifier for a task number."""
    verifier_path = BENCHMARK_DIR / f"task_{task_num:02d}_success_criteria.py"
    if verifier_path.exists():
        return verifier_path
    return None


def read_benchmark_verifier(task_num: int) -> Optional[str]:
    """Read the benchmark verifier source code."""
    path = get_benchmark_verifier_path(task_num)
    if path:
        with open(path, 'r') as f:
            return f.read()
    return None


def classify_task_type(yaml_data: Dict, thresholds: Dict) -> str:
    """Classify task type based on YAML content and extracted thresholds.

    Returns: 'inventory', 'agent_specific', 'combat', 'hybrid', 'resource'
    """
    has_kills = bool(thresholds.get('kills'))
    has_agent_items = bool(thresholds.get('agent_items'))
    has_items = bool(thresholds.get('items')) or bool(thresholds.get('has_items'))

    if has_kills and (has_items or has_agent_items):
        return 'hybrid'
    elif has_kills:
        return 'combat'
    elif has_agent_items:
        return 'agent_specific'
    elif has_items:
        return 'inventory'
    else:
        return 'inventory'  # Default


def generate_verifier_code(
    task_num: int,
    task_name: str,
    variant: str,
    yaml_data: Dict,
    thresholds: Dict,
    task_type: str
) -> str:
    """Generate the verifier Python code for an augmented task."""

    filename = f"task_{task_num:02d}_{task_name}_{variant}_success_criteria.py"
    source_yaml = f"task_{task_num:02d}_{task_name}_{variant}.yaml"

    # Build the import statement
    imports = [
        "get_final_inventories",
        "count_item_in_inventories",
        "has_item_in_any_inventory",
        "check_agents_alive",
    ]

    if task_type in ('combat', 'hybrid'):
        imports.append("count_combat_kills")

    if task_type == 'agent_specific':
        imports.append("get_agent_items_by_username")

    imports_str = ",\n    ".join(imports)

    # Get task description from YAML
    task_desc = yaml_data.get('task', {}).get('name', f'Task {task_num}')
    primary_obj = yaml_data.get('objectives', {}).get('primary', '')

    # Generate verification logic based on task type
    if task_type == 'agent_specific':
        verification_code = generate_agent_specific_logic(thresholds)
    elif task_type == 'combat':
        verification_code = generate_combat_logic(thresholds)
    elif task_type == 'hybrid':
        verification_code = generate_hybrid_logic(thresholds)
    else:  # inventory
        verification_code = generate_inventory_logic(thresholds)

    template = f'''"""
Task {task_num:02d} {task_name.replace('_', ' ').title()} {variant.upper()} Success Criteria Verifier
Generated from: {source_yaml}
Description: {task_desc}
"""

import sys
from pathlib import Path

# Add benchmark directory to path for verifier_utils
sys.path.insert(0, str(Path(__file__).parent.parent / "v1.3_benchmark"))

from typing import Dict, Tuple
from verifier_utils import (
    {imports_str},
)


def verify(traj_json: Dict) -> Tuple[int, str]:
    """
    {task_desc}

    Primary objective: {primary_obj}
    """
{verification_code}


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python {filename} <trajectory.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        traj = json.load(f)

    success, msg = verify(traj)
    print(f"Success: {{success}}")
    print(f"Message: {{msg}}")
'''
    return template


def generate_inventory_logic(thresholds: Dict) -> str:
    """Generate inventory-based verification logic."""
    lines = ["    inventories = get_final_inventories(traj_json)"]
    checks = []
    msg_parts = []

    # Check for specific item counts
    for item, count in thresholds.get('items', {}).items():
        var_name = item.replace(' ', '_')
        lines.append(f"    {var_name}_count = count_item_in_inventories(inventories, '{item}')")
        checks.append(f"{var_name}_count >= {count}")
        msg_parts.append(f"{item}: {{{var_name}_count}}/{count}")

    # Check for items that just need to exist
    for item in thresholds.get('has_items', []):
        var_name = item.replace(' ', '_')
        lines.append(f"    has_{var_name} = has_item_in_any_inventory(inventories, '{item}')")
        checks.append(f"has_{var_name}")
        msg_parts.append(f"{item}: {{has_{var_name}}}")

    # Check survival
    if thresholds.get('check_alive'):
        lines.append("    alive = check_agents_alive(traj_json)")
        checks.append("alive")
        msg_parts.append("alive: {alive}")

    lines.append("")

    if checks:
        lines.append(f"    passed = {' and '.join(checks)}")
    else:
        lines.append("    passed = True")

    if msg_parts:
        lines.append(f'    msg = f"{", ".join(msg_parts)}"')
    else:
        lines.append('    msg = "No specific criteria"')

    lines.append("    return (1 if passed else 0, msg)")

    return "\n".join(lines)


def generate_agent_specific_logic(thresholds: Dict) -> str:
    """Generate agent-specific inventory verification logic."""
    lines = ["    agent_items = get_agent_items_by_username(traj_json)"]
    checks = []
    msg_parts = []

    for agent, items in thresholds.get('agent_items', {}).items():
        # Extract agent pattern for matching (e.g., corn_harvester from corn_harvester_agent)
        agent_pattern = agent.replace('_agent', '')
        lines.append(f"")
        lines.append(f"    # Find {agent}'s inventory")
        lines.append(f"    {agent_pattern}_items = {{}}")
        lines.append(f"    for username, items in agent_items.items():")
        lines.append(f'        if "{agent_pattern}" in username.lower():')
        lines.append(f"            {agent_pattern}_items = items")
        lines.append(f"            break")

        for item, count in items.items():
            var_name = f"{agent_pattern}_{item}"
            lines.append(f'    {var_name} = {agent_pattern}_items.get("{item}", 0)')
            checks.append(f"{var_name} >= {count}")
            msg_parts.append(f"{item}({agent_pattern}): {{{var_name}}}/{count}")

    # Check survival
    if thresholds.get('check_alive'):
        lines.append("")
        lines.append("    alive = check_agents_alive(traj_json)")
        checks.append("alive")
        msg_parts.append("alive: {alive}")

    lines.append("")

    if checks:
        lines.append(f"    passed = {' and '.join(checks)}")
    else:
        lines.append("    passed = True")

    if msg_parts:
        lines.append(f'    msg = f"{", ".join(msg_parts)}"')
    else:
        lines.append('    msg = "No specific criteria"')

    lines.append("    return (1 if passed else 0, msg)")

    return "\n".join(lines)


def generate_combat_logic(thresholds: Dict) -> str:
    """Generate combat-based verification logic."""
    lines = []
    checks = []
    msg_parts = []

    kills = thresholds.get('kills', {})
    if kills:
        target_list = list(kills.keys())
        total_kills = sum(kills.values())
        targets_str = str(target_list)

        lines.append(f"    # Combat targets: {kills}")
        lines.append(f"    kills = count_combat_kills(traj_json, {targets_str})")
        checks.append(f"kills >= {total_kills}")
        msg_parts.append(f"kills: {{kills}}/{total_kills}")

    # Check survival
    if thresholds.get('check_alive'):
        lines.append("    alive = check_agents_alive(traj_json)")
        checks.append("alive")
        msg_parts.append("alive: {alive}")

    lines.append("")

    if checks:
        lines.append(f"    passed = {' and '.join(checks)}")
    else:
        lines.append("    passed = True")

    if msg_parts:
        lines.append(f'    msg = f"{", ".join(msg_parts)}"')
    else:
        lines.append('    msg = "No specific criteria"')

    lines.append("    return (1 if passed else 0, msg)")

    return "\n".join(lines)


def generate_hybrid_logic(thresholds: Dict) -> str:
    """Generate hybrid (combat + inventory) verification logic."""
    lines = ["    inventories = get_final_inventories(traj_json)"]
    checks = []
    msg_parts = []

    # Inventory checks
    for item, count in thresholds.get('items', {}).items():
        var_name = item.replace(' ', '_')
        lines.append(f"    {var_name}_count = count_item_in_inventories(inventories, '{item}')")
        checks.append(f"{var_name}_count >= {count}")
        msg_parts.append(f"{item}: {{{var_name}_count}}/{count}")

    # Combat checks
    kills = thresholds.get('kills', {})
    if kills:
        target_list = list(kills.keys())
        total_kills = sum(kills.values())
        targets_str = str(target_list)

        lines.append(f"")
        lines.append(f"    # Combat targets: {kills}")
        lines.append(f"    kills = count_combat_kills(traj_json, {targets_str})")
        checks.append(f"kills >= {total_kills}")
        msg_parts.append(f"kills: {{kills}}/{total_kills}")

    # Check survival
    if thresholds.get('check_alive'):
        lines.append("    alive = check_agents_alive(traj_json)")
        checks.append("alive")
        msg_parts.append("alive: {alive}")

    lines.append("")

    if checks:
        lines.append(f"    passed = {' and '.join(checks)}")
    else:
        lines.append("    passed = True")

    if msg_parts:
        lines.append(f'    msg = f"{", ".join(msg_parts)}"')
    else:
        lines.append('    msg = "No specific criteria"')

    lines.append("    return (1 if passed else 0, msg)")

    return "\n".join(lines)


def generate_verifier_for_yaml(yaml_path: Path) -> Tuple[str, str]:
    """Generate a verifier file for an augmented task YAML.

    Returns (output_filename, generated_code).
    """
    # Parse task info
    task_num, task_name, variant = extract_task_info(yaml_path)

    # Parse YAML
    yaml_data = parse_yaml_file(yaml_path)

    # Extract success criteria
    criteria = yaml_data.get('success_criteria', [])
    if not criteria:
        criteria = []

    # Extract thresholds
    thresholds = extract_thresholds_from_criteria(criteria)

    # Classify task type
    task_type = classify_task_type(yaml_data, thresholds)

    # Generate code
    code = generate_verifier_code(
        task_num, task_name, variant, yaml_data, thresholds, task_type
    )

    # Output filename
    output_filename = f"task_{task_num:02d}_{task_name}_{variant}_success_criteria.py"

    return output_filename, code


def main():
    """Main entry point - generate verifiers for all augmented tasks."""
    print(f"Scanning {AUGMENTED_DIR} for YAML files...")

    yaml_files = sorted(AUGMENTED_DIR.glob("task_*.yaml"))
    print(f"Found {len(yaml_files)} YAML files")

    generated = 0
    errors = []

    for yaml_path in yaml_files:
        try:
            output_filename, code = generate_verifier_for_yaml(yaml_path)
            output_path = AUGMENTED_DIR / output_filename

            with open(output_path, 'w') as f:
                f.write(code)

            generated += 1
            print(f"  Generated: {output_filename}")

        except Exception as e:
            errors.append((yaml_path.name, str(e)))
            print(f"  ERROR: {yaml_path.name}: {e}")

    print(f"\nGeneration complete!")
    print(f"  Generated: {generated} files")
    print(f"  Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for filename, error in errors:
            print(f"  {filename}: {error}")


if __name__ == "__main__":
    main()
