"""
Action Proposer Module

Uses the Claude Agent SDK for Claude model inference.
No API key needed - uses Claude Code's authentication.
"""

import json
import re
import os
import asyncio
from typing import Dict, List, Any, Optional

# Import Claude Agent SDK
from claude_agent_sdk import query, ClaudeAgentOptions

# Model configuration - use Claude Sonnet 4.5 for best reasoning
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")


# Action type definitions for prompts
ACTION_TYPES = """
Available action types:
1. move: {"type": "move", "x": <number>, "y": <number>, "pickupItems": [{"key": "<item>", "count": <number>}, ...]} - Move to coordinates
   - This reflects real game behavior where items are auto-collected when walking over them
   - pickupItems is OPTIONAL - only include when picking up dropped items
   - Use pickupItems when another agent has dropped items at the destination
   - Example without pickup: {"type": "move", "x": 100, "y": 50}
   - Example with pickup: {"type": "move", "x": 100, "y": 50, "pickupItems": [{"key": "logs", "count": 2}]}
2. craft: type=craft, skill=<skill>, itemKey=<item>, count=<number> - Craft an item
   - Skills: Smelting, Smithing, Fletching, Cooking, Crafting
   - itemKey must be lowercase SINGULAR (e.g., "ironbar", "stick", "arrow" - NOT "arrows", NOT "sticks")
   - IMPORTANT: count determines how many to craft. Use count=10 to craft 10 arrows at once!
3. collect: {"type": "collect", "resourceType": "<tree|rock|fish|foraging>", "resourceKey": "<key>"} - Collect from resource
   - IMPORTANT: resourceKey must be LOWERCASE and match the key shown in observations
   - Examples: "oak", "oak2", "oak3", "iron", "coal", "copper"
   - Look for the key="..." in the resource listing
4. attack: {"type": "attack", "targetInstance": "<instance>"} - Attack a target
5. equip: {"type": "equip", "inventoryIndex": <number>} - Equip item from inventory
6. unequip: {"type": "unequip", "equipmentSlot": <number>} - Unequip to inventory
7. eat: {"type": "eat", "inventoryIndex": <number>} - Eat food for healing
8. drop: {"type": "drop", "inventoryIndex": <number>, "count": <optional number>} - Drop item on ground for another agent to pick up
9. use: {"type": "use", "inventoryIndex": <number>} - Use consumable item
10. enter: {"type": "enter"} - Enter warp/portal at current position
11. wait: {"type": "wait"} - Do nothing this turn (placeholder action)
12. transfer: {"type": "transfer", "targetPlayer": "<agent_name>", "itemKey": "<item>", "count": <number>} - Transfer items to another agent
   - Directly transfers items from your inventory to the target agent's inventory
   - Both agents must exist in the same game session
   - Example: {"type": "transfer", "targetPlayer": "smith_agent", "itemKey": "ironbar", "count": 2}

ITEM TRANSFER BETWEEN AGENTS:
Use the "transfer" action to directly give items to another agent:
  {"type": "transfer", "targetPlayer": "target_agent_name", "itemKey": "itemname", "count": N}
This is the PREFERRED method for moving items between agents.
"""


async def call_claude_async(prompt: str, max_tokens: int = 4096, use_haiku: bool = False) -> str:
    """
    Call Claude using the Claude Agent SDK (async version).

    Args:
        prompt: The prompt to send to Claude
        max_tokens: Maximum tokens for response
        use_haiku: If True, use Haiku model for faster/cheaper calls

    Returns:
        Claude's response as a string
    """
    # Select model based on use_haiku flag
    model = "claude-3-5-haiku-20241022" if use_haiku else CLAUDE_MODEL

    try:
        result_text = ""
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=[],  # No tools needed for simple text completion
                model=model,
            )
        ):
            # Extract text from assistant messages
            if hasattr(message, 'message') and message.message:
                content = message.message.content if hasattr(message.message, 'content') else []
                for block in content:
                    if hasattr(block, 'text'):
                        result_text += block.text
            # Also check for direct text content
            elif hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        result_text += block.text
        return result_text
    except Exception as e:
        return f"Error calling Claude Agent SDK: {str(e)}"


def call_claude(prompt: str, max_tokens: int = 4096, use_haiku: bool = False) -> str:
    """
    Call Claude using the Claude Agent SDK (sync wrapper).

    Args:
        prompt: The prompt to send to Claude
        max_tokens: Maximum tokens for response
        use_haiku: If True, use Haiku model for faster/cheaper calls

    Returns:
        Claude's response as a string
    """
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # We're in an async context, create a new thread to run the async code
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(call_claude_async(prompt, max_tokens, use_haiku))
                )
                return future.result(timeout=120)
        else:
            # No event loop, we can use asyncio.run directly
            return asyncio.run(call_claude_async(prompt, max_tokens, use_haiku))
    except Exception as e:
        return f"Error: {str(e)}"


def summarize_team_inventory(agent_states: Dict[str, Dict[str, Any]]) -> str:
    """Summarize total items across all agents for goal tracking."""
    totals = {}
    fletcher_sticks = 0
    fletcher_feathers = 0

    for agent_name, state in agent_states.items():
        is_fletcher = 'fletcher' in agent_name.lower()
        for item in state.get('inventory', []) or []:
            if item and isinstance(item, dict):
                key = item.get('key', '').lower()
                count = item.get('count', 1)
                # Ensure count is a valid integer (handle None or NaN)
                if count is None or (isinstance(count, float) and str(count) == 'nan'):
                    count = 1
                totals[key] = totals.get(key, 0) + int(count)
                if is_fletcher:
                    if key == 'stick':
                        fletcher_sticks += int(count)
                    elif key == 'feather':
                        fletcher_feathers += int(count)

    if not totals:
        return "Team has no items."

    items_str = ", ".join(f"{k}x{v}" for k, v in sorted(totals.items()) if v > 0)
    result = f"TEAM TOTAL: {items_str}"
    result += f" | FLETCHER: sticks={fletcher_sticks}, feathers={fletcher_feathers}"

    # Add milestone alerts for common goals
    arrows = totals.get('arrow', 0)

    if arrows >= 10:
        result += "\n>>> GOAL ACHIEVED: Team has 10+ arrows!"
    elif fletcher_sticks >= 10 and fletcher_feathers >= 10:
        result += f"\n>>> READY TO CRAFT ARROWS NOW!"

    return result


def format_state_for_prompt(agent_name: str, state: Dict[str, Any], compact: bool = True) -> str:
    """Format an agent's state for inclusion in a prompt."""
    if not state:
        return f"### {agent_name}: Unknown state\n"

    # Get inventory items (non-null only) - compact format
    inventory_items = []
    for i, item in enumerate(state.get('inventory', []) or []):
        if item and isinstance(item, dict):
            if compact:
                inventory_items.append(f"[{i}]{item.get('key', '?')}x{item.get('count', 1)}")
            else:
                inventory_items.append(f"  [{i}] {item.get('key', '?')} x{item.get('count', 1)}")

    # Get equipment - compact format
    equipment_items = []
    slot_abbrev = {0: 'A', 1: 'B', 2: 'P', 3: 'R', 4: 'W', 5: 'Ar'}
    slot_names = {0: 'Armour', 1: 'Boots', 2: 'Pendant', 3: 'Ring', 4: 'Weapon', 5: 'Arrows'}
    for slot, item in (state.get('equipment', {}) or {}).items():
        if item and isinstance(item, dict):
            if compact:
                equipment_items.append(f"{slot_abbrev.get(int(slot), slot)}:{item.get('key', '?')}")
            else:
                equipment_items.append(f"  {slot_names.get(int(slot), slot)}: {item.get('key', '?')}")

    x, y = state.get('x', '?'), state.get('y', '?')
    hp = state.get('hitPoints', '?')
    max_hp = state.get('maxHitPoints', '?')

    if compact:
        # Ultra-compact format
        inv_str = ', '.join(inventory_items) if inventory_items else 'empty'
        equip_str = ', '.join(equipment_items) if equipment_items else 'none'
        return f"### {agent_name} @({x},{y}) HP:{hp}/{max_hp}\nInv: {inv_str}\nEquip: {equip_str}\n"
    else:
        # Format skills (only in non-compact mode)
        skill_names_map = {
            0: 'Lumberjacking', 1: 'Accuracy', 2: 'Archery', 3: 'Health',
            4: 'Magic', 5: 'Mining', 6: 'Strength', 7: 'Defense',
            8: 'Fishing', 9: 'Cooking', 10: 'Smithing', 11: 'Crafting',
            12: 'Fletching', 14: 'Foraging'
        }
        skills_str = []
        for skill_type, exp in state.get('skills', {}).items():
            if exp is None:
                continue
            name = skill_names_map.get(int(skill_type), f'Skill{skill_type}')
            level = 1
            for lvl, req_exp in enumerate([0, 83, 174, 276, 388, 512, 650, 801, 969, 1154, 1358, 1584, 1833, 2107, 2411]):
                if exp >= req_exp:
                    level = lvl + 1
            skills_str.append(f"{name}:{level}")

        result = f"""### {agent_name}
- Position: ({x}, {y})
- HP: {hp}/{max_hp}
- Skills: {', '.join(skills_str) if skills_str else 'None'}
- Inventory:
{chr(10).join(inventory_items) if inventory_items else '  (empty)'}
- Equipment:
{chr(10).join(equipment_items) if equipment_items else '  (none)'}
"""
        return result


def get_resource_key(resource: Dict[str, Any]) -> str:
    """Extract the resource key from the resource name (lowercase first word)."""
    name = resource.get('name', '')
    # Extract first word and convert to lowercase
    # e.g., "Oak2 Tree" -> "oak2", "Iron Rock" -> "iron"
    if name:
        first_word = name.split()[0] if name.split() else ''
        return first_word.lower()
    return ''


def format_observation_for_prompt(agent_name: str, obs: Dict[str, Any], compact: bool = True) -> str:
    """Format an observation for inclusion in a prompt.

    Args:
        agent_name: Name of the agent
        obs: Observation dict from API
        compact: If True, use minimal format to reduce tokens
    """
    location = obs.get('location', {})
    x, y = location.get('x', '?'), location.get('y', '?')

    if compact:
        # Compact format - minimal tokens
        lines = [f"### {agent_name} at ({x},{y})"]
    else:
        lines = [f"### {agent_name}'s Observation"]
        lines.append(f"- Current Position: ({x}, {y})")
        lines.append(f"- Region: {location.get('mapName', 'Unknown')}")
        radius = obs.get('observationRadius', 15)
        lines.append(f"- Vision Radius: {radius} tiles")

    # Resources - only show nearby ones (distance <= 10), compact format
    resources = obs.get('resources', [])
    if resources:
        resources_sorted = sorted(resources, key=lambda r: r.get('distanceFrom', 999))
        # Filter to only nearby resources
        nearby = [r for r in resources_sorted if r.get('distanceFrom', 999) <= 10][:5]

        if compact and nearby:
            # Ultra-compact: "Resources: oak2@(229,32)d=5, iron@(240,38)d=8"
            res_parts = []
            for r in nearby:
                key = get_resource_key(r)
                d = int(r.get('distanceFrom', 0))
                res_parts.append(f"{key}@({r['x']},{r['y']})d={d}")
            lines.append(f"Resources: {', '.join(res_parts)}")
        elif nearby:
            lines.append(f"\n- Nearby Resources:")
            for r in nearby:
                key = get_resource_key(r)
                d = int(r.get('distanceFrom', 0))
                lines.append(f"  {key} at ({r['x']},{r['y']}) [{d}t]")

    # Mobs - only show aggressive ones in compact mode
    mobs = obs.get('mobs', [])
    if mobs:
        if compact:
            aggressive_mobs = [m for m in mobs if m.get('aggressive') and m.get('distanceFrom', 999) <= 10]
            if aggressive_mobs:
                mob_parts = [f"{m['name']}@({m['x']},{m['y']})" for m in aggressive_mobs[:3]]
                lines.append(f"Threats: {', '.join(mob_parts)}")
        else:
            mobs_sorted = sorted(mobs, key=lambda m: m.get('distanceFrom', 999))[:5]
            lines.append(f"\n- Enemies ({len(mobs)}):")
            for m in mobs_sorted:
                agg = "!" if m.get('aggressive') else ""
                lines.append(f"  {m['name']}{agg} at ({m['x']},{m['y']})")

    # Other players - only if nearby
    players = obs.get('players', [])
    if players:
        nearby_players = [p for p in players if p.get('distanceFrom', 999) <= 5]
        if nearby_players:
            if compact:
                p_parts = [f"{p['name']}@({p['x']},{p['y']})" for p in nearby_players[:3]]
                lines.append(f"Nearby players: {', '.join(p_parts)}")
            else:
                for p in nearby_players[:3]:
                    lines.append(f"  Player {p['name']} at ({p['x']},{p['y']})")

    # Skip doors, warps, and collision info in compact mode - rarely needed for crafting tasks

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

    # Debug: log if we got fewer action sets than requested
    if len(action_sets) < beam_count:
        print(f"    [DEBUG] Requested {beam_count} action sets, got {len(action_sets)}")
        print(f"    [DEBUG] Response preview: {response[:500]}...")

    return action_sets


def propose_actions_multi_branch(
    task_context: str,
    branches: List[Dict[str, Any]],
    beam_count: int = 2
) -> Dict[int, List[Dict[str, Dict[str, Any]]]]:
    """
    Propose actions for multiple branches in a single Claude call.

    Prompt structure optimized for cache hits:
    1. Static content first (action types, task context, instructions)
    2. Dynamic content last (branch states)

    Args:
        task_context: Description of the task and objectives
        branches: List of branch data, each containing:
            - agent_states: Current state for each agent
            - observations: Current observations for each agent
            - history: List of previous action results
        beam_count: Number of different action sets to propose per branch

    Returns:
        Dict mapping branch index to list of action sets
    """
    if not branches:
        return {}

    agent_names = list(branches[0]['agent_states'].keys())

    # === STATIC CONTENT FIRST (for cache hits) ===
    prompt = f"""You are an AI assistant helping to solve a multi-agent cooperative game task.

{ACTION_TYPES}

## Task Objective

{task_context}

## Instructions

You will be given game states for multiple branches. For EACH branch, propose {beam_count} different action strategies.

IMPORTANT:
- Each agent must have exactly one action per strategy
- Use "wait" if an agent should not do anything
- Make strategies diverse within each branch
- resourceKey must be LOWERCASE (e.g., "oak", "iron", not "Oak", "Iron")
- Respond with ONLY valid JSON

GOAL-ORIENTED THINKING:
- BEFORE proposing actions, check: Can the FINAL GOAL be achieved NOW with current items?
- If you have enough materials for the final craft/equip, DO IT - don't keep gathering more!
- Don't get stuck in loops making intermediate items when you already have enough

COMMON RECIPES (check if you have enough materials!):
- stick: 1x logs → 4x sticks (craft skill=Fletching itemKey=stick)
- arrows: 10x sticks + 10x feathers → 10x arrows (craft skill=Fletching itemKey=arrow)
  * NOTE: itemKey is "arrow" (singular), NOT "arrows"!
  * DO NOT use count parameter - game auto-produces 10 arrows from 10 sticks + 10 feathers
- staff: 5x stick + 1x bead → 1x staff (craft skill=Crafting itemKey=staff)

CRITICAL: When "READY TO CRAFT ARROWS" appears, fletcher MUST craft arrows!
The correct action format: type=craft, skill=Fletching, itemKey=arrow (NO count parameter needed!)

Response format - a JSON object mapping branch numbers to action arrays:
```json
{{
  "1": [
    {{"agent1": {{"type": "move", "x": 100, "y": 50}}, "agent2": {{"type": "collect", "resourceType": "tree", "resourceKey": "oak"}}}},
    {{"agent1": {{"type": "wait"}}, "agent2": {{"type": "craft", "skill": "Smithing", "itemKey": "ironbar", "count": 1}}}}
  ],
  "2": [
    {{"agent1": {{"type": "drop", "inventoryIndex": 0}}, "agent2": {{"type": "move", "x": 200, "y": 100}}}},
    {{"agent1": {{"type": "collect", "resourceType": "rock", "resourceKey": "iron"}}, "agent2": {{"type": "wait"}}}}
  ]
}}
```

## Current Game States

"""

    # === DYNAMIC CONTENT LAST ===
    for branch_idx, branch in enumerate(branches):
        prompt += f"### Branch {branch_idx + 1}\n"

        # Add team inventory summary for goal tracking
        prompt += summarize_team_inventory(branch['agent_states']) + "\n\n"

        prompt += "Agent States:\n"
        for agent_name, state in branch['agent_states'].items():
            prompt += format_state_for_prompt(agent_name, state)

        prompt += "Observations:\n"
        for agent_name, obs in branch['observations'].items():
            prompt += format_observation_for_prompt(agent_name, obs)

        history = branch.get('history', [])
        if history:
            prompt += f"Recent History:\n{format_history_for_prompt(history, max_steps=2)}\n"
        prompt += "\n"

    prompt += f"Provide actions for all {len(branches)} branch(es) as JSON:"

    # Call Claude
    response = call_claude(prompt)

    # Parse the response
    result = parse_multi_branch_actions(response, agent_names, len(branches), beam_count)

    return result


def parse_multi_branch_actions(
    response: str,
    agent_names: List[str],
    num_branches: int,
    expected_count: int
) -> Dict[int, List[Dict[str, Dict[str, Any]]]]:
    """
    Parse Claude's response for multi-branch action proposals.

    Returns:
        Dict mapping branch index (0-based) to list of action sets
    """
    result = {}

    # Try to find JSON object in response
    json_match = re.search(r'\{[\s\S]*\}', response)

    if json_match:
        try:
            data = json.loads(json_match.group())

            for branch_key in data:
                # Handle both "1" and 1 as keys
                branch_idx = int(branch_key) - 1  # Convert to 0-based index

                if 0 <= branch_idx < num_branches:
                    action_sets = data[branch_key]
                    if isinstance(action_sets, list):
                        cleaned_sets = []
                        for action_set in action_sets[:expected_count]:
                            if isinstance(action_set, dict):
                                cleaned = {}
                                for agent_name in agent_names:
                                    if agent_name in action_set:
                                        cleaned[agent_name] = action_set[agent_name]
                                    else:
                                        cleaned[agent_name] = {'type': 'wait'}
                                cleaned_sets.append(cleaned)
                        if cleaned_sets:
                            result[branch_idx] = cleaned_sets

        except (json.JSONDecodeError, ValueError, KeyError):
            pass

    # Fill in missing branches with default actions
    for i in range(num_branches):
        if i not in result:
            result[i] = [_default_action_sets(agent_names, 1)[0]]

    return result


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
