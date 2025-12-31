"""
Action Proposer Module

Uses Claude CLI to propose actions for agents based on task context and current state.
"""

import subprocess
import json
import re
from typing import Dict, List, Any, Optional


# Action type definitions for prompts
ACTION_TYPES = """
Available action types:
1. move: {"type": "move", "x": <number>, "y": <number>} - Move to coordinates
2. craft: {"type": "craft", "skill": "<skill>", "itemKey": "<item>", "count": <number>} - Craft an item
3. collect: {"type": "collect", "resourceType": "<tree|rock|fish|foraging>", "resourceKey": "<resource>"} - Collect from resource
4. attack: {"type": "attack", "targetInstance": "<instance>"} - Attack a target
5. equip: {"type": "equip", "inventoryIndex": <number>} - Equip item from inventory
6. unequip: {"type": "unequip", "equipmentSlot": <number>} - Unequip to inventory
7. eat: {"type": "eat", "inventoryIndex": <number>} - Eat food for healing
8. drop: {"type": "drop", "inventoryIndex": <number>, "count": <optional number>} - Drop item
9. use: {"type": "use", "inventoryIndex": <number>} - Use consumable item
10. enter: {"type": "enter"} - Enter warp/portal at current position
11. wait: {"type": "wait"} - Do nothing this turn (placeholder action)
"""


def call_claude(prompt: str, max_tokens: int = 4096) -> str:
    """
    Call Claude CLI with a prompt and return the response.

    Args:
        prompt: The prompt to send to Claude
        max_tokens: Maximum tokens for response

    Returns:
        Claude's response as a string
    """
    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--output-format', 'json'],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            # Try to extract error message
            error_msg = result.stderr or result.stdout or "Unknown error"
            return f"Error calling Claude CLI: {error_msg}"

        # Parse JSON output
        try:
            response = json.loads(result.stdout)
            return response.get('result', '')
        except json.JSONDecodeError:
            # If not JSON, return raw output
            return result.stdout

    except subprocess.TimeoutExpired:
        return "Error: Claude CLI timed out"
    except FileNotFoundError:
        return "Error: Claude CLI not found. Make sure 'claude' is in PATH."
    except Exception as e:
        return f"Error calling Claude CLI: {str(e)}"


def format_state_for_prompt(agent_name: str, state: Dict[str, Any]) -> str:
    """Format an agent's state for inclusion in a prompt."""
    if not state:
        return f"### {agent_name}\n- State: Unknown\n"

    # Get inventory items (non-null only)
    inventory_items = []
    for i, item in enumerate(state.get('inventory', []) or []):
        if item and isinstance(item, dict):
            inventory_items.append(f"  [{i}] {item.get('key', '?')} x{item.get('count', 1)}")

    # Get equipment
    equipment_items = []
    slot_names = {0: 'Armour', 1: 'Boots', 2: 'Pendant', 3: 'Ring', 4: 'Weapon', 5: 'Arrows'}
    for slot, item in (state.get('equipment', {}) or {}).items():
        if item and isinstance(item, dict):
            equipment_items.append(f"  {slot_names.get(int(slot), slot)}: {item.get('key', '?')}")

    # Format skills
    skill_names = {
        0: 'Lumberjacking', 1: 'Accuracy', 2: 'Archery', 3: 'Health',
        4: 'Magic', 5: 'Mining', 6: 'Strength', 7: 'Defense',
        8: 'Fishing', 9: 'Cooking', 10: 'Smithing', 11: 'Crafting',
        12: 'Fletching', 14: 'Foraging'
    }
    skills_str = []
    for skill_type, exp in state.get('skills', {}).items():
        if exp is None:
            continue
        name = skill_names.get(int(skill_type), f'Skill{skill_type}')
        # Rough level estimate (simplified)
        level = 1
        for lvl, req_exp in enumerate([0, 83, 174, 276, 388, 512, 650, 801, 969, 1154, 1358, 1584, 1833, 2107, 2411]):
            if exp >= req_exp:
                level = lvl + 1
        skills_str.append(f"{name}:{level}")

    result = f"""### {agent_name}
- Position: ({state.get('x', '?')}, {state.get('y', '?')})
- HP: {state.get('hitPoints', '?')}/{state.get('maxHitPoints', '?')}
- Mana: {state.get('mana', '?')}/{state.get('maxMana', '?')}
- Dead: {state.get('dead', False)}
- Skills: {', '.join(skills_str) if skills_str else 'None'}
- Inventory:
{chr(10).join(inventory_items) if inventory_items else '  (empty)'}
- Equipment:
{chr(10).join(equipment_items) if equipment_items else '  (none)'}
"""
    return result


def format_observation_for_prompt(agent_name: str, obs: Dict[str, Any]) -> str:
    """Format an observation for inclusion in a prompt."""
    lines = [f"### {agent_name}'s Observation"]

    # Location info
    location = obs.get('location', {})
    if location:
        lines.append(f"- Current Position: ({location.get('x', '?')}, {location.get('y', '?')})")
        lines.append(f"- Region: {location.get('mapName', 'Unknown')}")

    # Observation radius
    radius = obs.get('observationRadius', 15)
    lines.append(f"- Vision Radius: {radius} tiles")

    # Resources - sorted by distance, grouped by type
    resources = obs.get('resources', [])
    if resources:
        # Sort by distance
        resources_sorted = sorted(resources, key=lambda r: r.get('distanceFrom', 999))

        # Group by resource type
        trees = [r for r in resources_sorted if r.get('resourceType') == 'tree']
        rocks = [r for r in resources_sorted if r.get('resourceType') == 'rock']
        fish = [r for r in resources_sorted if r.get('resourceType') == 'fish']
        foraging = [r for r in resources_sorted if r.get('resourceType') == 'foraging']

        lines.append(f"\n- Resources Visible ({len(resources)} total):")

        if trees:
            lines.append(f"  Trees ({len(trees)}):")
            for r in trees[:8]:
                dist = r.get('distanceFrom', 0)
                status = "REACHABLE" if dist <= 2 else f"{dist:.0f} tiles away"
                lines.append(f"    - {r['name']} at ({r['x']},{r['y']}) [{status}]")

        if rocks:
            lines.append(f"  Rocks ({len(rocks)}):")
            for r in rocks[:5]:
                dist = r.get('distanceFrom', 0)
                status = "REACHABLE" if dist <= 2 else f"{dist:.0f} tiles away"
                lines.append(f"    - {r['name']} at ({r['x']},{r['y']}) [{status}]")

        if fish:
            lines.append(f"  Fishing Spots ({len(fish)}):")
            for r in fish[:5]:
                dist = r.get('distanceFrom', 0)
                lines.append(f"    - {r['name']} at ({r['x']},{r['y']}) [{dist:.0f} tiles]")

        if foraging:
            lines.append(f"  Foraging ({len(foraging)}):")
            for r in foraging[:5]:
                dist = r.get('distanceFrom', 0)
                lines.append(f"    - {r['name']} at ({r['x']},{r['y']}) [{dist:.0f} tiles]")
    else:
        lines.append("\n- Resources Visible: None nearby")

    # Mobs - sorted by distance
    mobs = obs.get('mobs', [])
    if mobs:
        mobs_sorted = sorted(mobs, key=lambda m: m.get('distanceFrom', 999))
        lines.append(f"\n- Enemies Visible ({len(mobs)}):")
        for m in mobs_sorted[:8]:
            dist = m.get('distanceFrom', 0)
            aggressive = "AGGRESSIVE" if m.get('aggressive') else "passive"
            lines.append(f"    - {m['name']} Lv{m['level']} at ({m['x']},{m['y']}) HP:{m['hitPoints']}/{m['maxHitPoints']} [{aggressive}, {dist:.0f} tiles]")

    # Other players
    players = obs.get('players', [])
    if players:
        players_sorted = sorted(players, key=lambda p: p.get('distanceFrom', 999))
        lines.append(f"\n- Other Players Visible ({len(players)}):")
        for p in players_sorted[:5]:
            dist = p.get('distanceFrom', 0)
            lines.append(f"    - {p['name']} Lv{p['level']} at ({p['x']},{p['y']}) [{dist:.0f} tiles]")

    # Doors (teleporters)
    doors = obs.get('doors', [])
    if doors:
        doors_sorted = sorted(doors, key=lambda d: d.get('distanceFrom', 999))
        lines.append(f"\n- Doors/Teleporters ({len(doors)}):")
        for d in doors_sorted[:5]:
            dist = d.get('distanceFrom', 0)
            lines.append(f"    - Door at ({d['x']},{d['y']}) -> ({d['destX']},{d['destY']}) [{dist:.0f} tiles]")

    # Warps/Entries
    entries = obs.get('entries', [])
    if entries:
        entries_sorted = sorted(entries, key=lambda e: e.get('distanceFrom', 999))
        lines.append(f"\n- Zone Warps ({len(entries)}):")
        for e in entries_sorted[:5]:
            dist = e.get('distanceFrom', 0)
            req = f"Lv{e['levelRequirement']}" if e.get('levelRequirement', 0) > 0 else "No req"
            lines.append(f"    - Warp to {e['destination']} at ({e['x']},{e['y']}) [{req}, {dist:.0f} tiles]")

    # Nearby blocked tiles (collision info)
    collisions = obs.get('collisions', [])
    if collisions:
        lines.append(f"\n- Blocked Tiles: {len(collisions)} nearby (avoid these coordinates)")

    return '\n'.join(lines)


def format_history_for_prompt(history: List[Dict[str, Any]], max_steps: int = 10) -> str:
    """Format action history for inclusion in a prompt."""
    if not history:
        return "No actions taken yet."

    lines = ["Recent actions:"]
    recent = history[-max_steps:] if len(history) > max_steps else history

    for i, step in enumerate(recent):
        step_num = len(history) - len(recent) + i + 1
        lines.append(f"\nStep {step_num}:")
        for agent_name, action_result in step.items():
            action = action_result.get('action', {})
            success = action_result.get('success', False)
            message = action_result.get('message', '')
            status = "OK" if success else "FAILED"
            lines.append(f"  {agent_name}: {action.get('type', 'unknown')} -> [{status}] {message[:50]}")

    return '\n'.join(lines)


def propose_actions(
    task_context: str,
    agent_states: Dict[str, Dict[str, Any]],
    observations: Dict[str, Dict[str, Any]],
    history: List[Dict[str, Any]],
    beam_count: int = 2
) -> List[Dict[str, Dict[str, Any]]]:
    """
    Call Claude CLI to propose multiple sets of actions for all agents.

    Args:
        task_context: Description of the task and objectives
        agent_states: Current state for each agent {name: state}
        observations: Current observations for each agent {name: obs}
        history: List of previous action results
        beam_count: Number of different action sets to propose

    Returns:
        List of action sets, each is {agent_name: action}
    """
    # Build the prompt
    prompt = f"""You are an AI assistant helping to solve a multi-agent cooperative game task.

{task_context}

## Current Agent States

"""
    for agent_name, state in agent_states.items():
        prompt += format_state_for_prompt(agent_name, state)
        prompt += "\n"

    prompt += "\n## Environment Observations\n\n"
    for agent_name, obs in observations.items():
        prompt += format_observation_for_prompt(agent_name, obs)
        prompt += "\n"

    prompt += f"\n## Action History\n\n{format_history_for_prompt(history)}\n"

    prompt += f"""

{ACTION_TYPES}

## Your Task

Propose {beam_count} different strategies (action sets) for this turn. Each strategy should specify one action for each agent.

Think about:
1. What resources are available nearby each agent
2. What items each agent needs to craft or collect
3. How agents should coordinate (e.g., one collects, another crafts)
4. The sequence of actions needed to achieve the objective

IMPORTANT:
- Each agent must have exactly one action
- Use "wait" action if an agent should not do anything this turn
- Make strategies diverse - explore different approaches
- Consider both short-term and long-term progress

Respond with ONLY a JSON array containing {beam_count} action sets. Each set is an object mapping agent names to their actions.

Example format:
```json
[
  {{
    "agent1_name": {{"type": "move", "x": 100, "y": 50}},
    "agent2_name": {{"type": "collect", "resourceType": "tree", "resourceKey": "Oak"}},
    "agent3_name": {{"type": "wait"}}
  }},
  {{
    "agent1_name": {{"type": "collect", "resourceType": "tree", "resourceKey": "Oak"}},
    "agent2_name": {{"type": "move", "x": 105, "y": 52}},
    "agent3_name": {{"type": "craft", "skill": "Fletching", "itemKey": "stick", "count": 1}}
  }}
]
```

Now provide your {beam_count} action sets as JSON:
"""

    # Call Claude
    response = call_claude(prompt)

    # Parse the response
    action_sets = parse_action_sets(response, list(agent_states.keys()), beam_count)

    return action_sets


def parse_action_sets(
    response: str,
    agent_names: List[str],
    expected_count: int
) -> List[Dict[str, Dict[str, Any]]]:
    """
    Parse Claude's response to extract action sets.

    Args:
        response: Claude's response string
        agent_names: List of expected agent names
        expected_count: Expected number of action sets

    Returns:
        List of action sets
    """
    # Try to find JSON in the response
    json_match = re.search(r'\[\s*\{.*?\}\s*\]', response, re.DOTALL)

    if json_match:
        try:
            action_sets = json.loads(json_match.group())
            if isinstance(action_sets, list):
                # Validate and clean up
                result = []
                for action_set in action_sets[:expected_count]:
                    if isinstance(action_set, dict):
                        cleaned = {}
                        for agent_name in agent_names:
                            if agent_name in action_set:
                                cleaned[agent_name] = action_set[agent_name]
                            else:
                                # Default to wait if agent not specified
                                cleaned[agent_name] = {'type': 'wait'}
                        result.append(cleaned)
                return result if result else _default_action_sets(agent_names, expected_count)
        except json.JSONDecodeError:
            pass

    # Fallback: try to extract individual JSON objects
    try:
        objects = re.findall(r'\{[^{}]*\}', response)
        if objects:
            action_sets = []
            current_set = {}
            for obj_str in objects:
                try:
                    obj = json.loads(obj_str)
                    if 'type' in obj:
                        # This looks like an action
                        for agent_name in agent_names:
                            if agent_name not in current_set:
                                current_set[agent_name] = obj
                                break
                        if len(current_set) == len(agent_names):
                            action_sets.append(current_set)
                            current_set = {}
                            if len(action_sets) >= expected_count:
                                break
                except json.JSONDecodeError:
                    continue
            if action_sets:
                return action_sets
    except Exception:
        pass

    # Default fallback
    return _default_action_sets(agent_names, expected_count)


def _default_action_sets(
    agent_names: List[str],
    count: int
) -> List[Dict[str, Dict[str, Any]]]:
    """Generate default wait actions for all agents."""
    default_set = {name: {'type': 'wait'} for name in agent_names}
    return [default_set.copy() for _ in range(count)]


if __name__ == '__main__':
    # Test the module
    print("Testing action proposer...")

    # Test calling Claude
    response = call_claude("Say 'Hello' in JSON format: {\"greeting\": \"...\"}")
    print(f"Claude response: {response[:200]}...")

    # Test parsing
    test_response = """
    Here are two strategies:
    ```json
    [
      {"agent1": {"type": "move", "x": 100, "y": 50}, "agent2": {"type": "wait"}},
      {"agent1": {"type": "wait"}, "agent2": {"type": "move", "x": 200, "y": 100}}
    ]
    ```
    """
    parsed = parse_action_sets(test_response, ['agent1', 'agent2'], 2)
    print(f"\nParsed action sets: {json.dumps(parsed, indent=2)}")
