#!/usr/bin/env python3
"""
Script to add ORE TYPE REFERENCE to mining-related tasks.
"""

import os
import re
from pathlib import Path

AUGMENTED_DIR = Path(__file__).parent / "v1.3_augmented"

ORE_REFERENCE = """
  ORE TYPE REFERENCE (CRITICAL - different rocks give different ores):
  - Iron Rock (around 545, 495): gives "ironore" (requires mining level 10+)
  - Nisoc Rock (around 336, 5): gives "nisocore" (NOT iron!)
  - Gold Rock (around 141, 5): gives "goldnugget" (requires mining level 25+)
  - Coal Rock: gives "coal" (requires mining level 1)
"""

def needs_ore_reference(content: str) -> bool:
    """Check if file mentions mining but lacks ORE TYPE REFERENCE."""
    has_mining = any(word in content.lower() for word in ['ironore', 'mining:', 'miner', 'goldnugget', 'coal'])
    has_reference = 'ORE TYPE REFERENCE' in content or 'ore type reference' in content.lower()
    return has_mining and not has_reference


def add_ore_reference(content: str) -> str:
    """Add ORE TYPE REFERENCE before max_action_steps."""
    # Find the position just before max_action_steps
    match = re.search(r'(\n\nmax_action_steps:|\nmax_action_steps:)', content)
    if match:
        pos = match.start()
        # Insert the reference before max_action_steps
        new_content = content[:pos] + ORE_REFERENCE + content[pos:]
        return new_content
    return content


def main():
    yaml_files = sorted(AUGMENTED_DIR.glob("*.yaml"))
    fixed = 0

    for yaml_path in yaml_files:
        with open(yaml_path, 'r') as f:
            content = f.read()

        if needs_ore_reference(content):
            new_content = add_ore_reference(content)
            if new_content != content:
                with open(yaml_path, 'w') as f:
                    f.write(new_content)
                print(f"Added ORE TYPE REFERENCE to: {yaml_path.name}")
                fixed += 1

    print(f"\nTotal files fixed: {fixed}")


if __name__ == "__main__":
    main()
