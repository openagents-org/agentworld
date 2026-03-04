#!/usr/bin/env python3
"""
Script to fix spawn locations for mining tasks.

Key locations:
- Gold Rock: (141, 5) - gives goldnugget
- Iron Rock: (545, 495) - gives ironore
- Coal Rock: (230, 45) - gives coal (in mining mountain area)
"""

import re
from pathlib import Path

AUGMENTED_DIR = Path(__file__).parent / "v1.3_augmented"

# Location fixes mapping
LOCATION_FIXES = {
    # Task 21 v2 - agents at (600, 500) need to mine goldnugget
    'task_21_mining_expedition_v2.yaml': {
        'ore_prospector_agent': {'x': 141, 'y': 10},      # Near Gold Rock
        'fuel_gatherer_agent': {'x': 230, 'y': 45},       # Near Coal Rock
        'mining_support_agent': {'x': 145, 'y': 10},      # Near Gold Rock
        'master_smith_agent': {'x': 235, 'y': 45},        # Near processing area
    },
}


def fix_spawn_location(content: str, agent_name: str, new_x: int, new_y: int) -> str:
    """Update spawn location for a specific agent."""
    # Pattern to find agent's location block
    # Looking for: username: "agent_name" ... location: ... x: OLD_X ... y: OLD_Y
    pattern = rf'(username:\s*"{agent_name}".*?location:\s*\n\s*x:\s*)(\d+)(\s*\n\s*y:\s*)(\d+)'

    def replace_coords(match):
        return f'{match.group(1)}{new_x}{match.group(3)}{new_y}'

    return re.sub(pattern, replace_coords, content, flags=re.DOTALL)


def main():
    fixed = 0

    for filename, agent_fixes in LOCATION_FIXES.items():
        yaml_path = AUGMENTED_DIR / filename
        if not yaml_path.exists():
            print(f"File not found: {filename}")
            continue

        with open(yaml_path, 'r') as f:
            content = f.read()

        original = content
        for agent_name, coords in agent_fixes.items():
            content = fix_spawn_location(content, agent_name, coords['x'], coords['y'])

        if content != original:
            with open(yaml_path, 'w') as f:
                f.write(content)
            print(f"Fixed spawn locations in: {filename}")
            for agent, coords in agent_fixes.items():
                print(f"  - {agent}: ({coords['x']}, {coords['y']})")
            fixed += 1

    print(f"\nTotal files fixed: {fixed}")


if __name__ == "__main__":
    main()
