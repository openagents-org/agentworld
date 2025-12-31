"""
Branch Evaluator Module

Uses Claude to evaluate and select the most promising branch in beam search.
"""

import json
import re
from typing import Dict, List, Any, Tuple

from .action_proposer import call_claude, format_state_for_prompt


def format_branch_for_prompt(
    branch_index: int,
    agent_states: Dict[str, Dict[str, Any]],
    last_actions: Dict[str, Dict[str, Any]],
    verifier_result: Tuple[bool, str]
) -> str:
    """Format a branch state for inclusion in evaluation prompt."""
    lines = [f"## Branch {branch_index + 1}"]

    # Last actions taken
    lines.append("\n### Last Actions:")
    for agent_name, action_result in last_actions.items():
        action = action_result.get('action', {})
        success = action_result.get('success', False)
        message = action_result.get('message', '')
        status = "✓" if success else "✗"
        lines.append(f"  - {agent_name}: {action.get('type', 'unknown')} [{status}] {message[:40]}")

    # Current states
    lines.append("\n### Current States:")
    for agent_name, state in agent_states.items():
        # Summarize inventory
        inventory_summary = []
        for item in state.get('inventory', []):
            if item and item.get('key'):
                inventory_summary.append(f"{item['key']}x{item['count']}")

        # Summarize equipment
        equipment_summary = []
        slot_names = {0: 'Armour', 1: 'Boots', 2: 'Pendant', 3: 'Ring', 4: 'Weapon', 5: 'Arrows'}
        for slot, item in state.get('equipment', {}).items():
            if item and item.get('key'):
                equipment_summary.append(f"{slot_names.get(int(slot), slot)}:{item['key']}")

        lines.append(f"  {agent_name}:")
        lines.append(f"    - Position: ({state['x']}, {state['y']})")
        lines.append(f"    - HP: {state['hitPoints']}/{state['maxHitPoints']}")
        lines.append(f"    - Inventory: {', '.join(inventory_summary) if inventory_summary else '(empty)'}")
        lines.append(f"    - Equipment: {', '.join(equipment_summary) if equipment_summary else '(none)'}")

    # Verifier result
    success, message = verifier_result
    lines.append(f"\n### Verification: {'SUCCESS' if success else 'Incomplete'}")
    lines.append(f"  Message: {message[:100]}")

    return '\n'.join(lines)


def evaluate_branches(
    task_context: str,
    branches: List[Dict[str, Any]],
    verifier_results: List[Tuple[bool, str]]
) -> int:
    """
    Call Claude to evaluate branches and select the most promising one.

    Args:
        task_context: Description of the task and objectives
        branches: List of branch states, each containing:
            - agent_states: Current states for all agents
            - last_actions: Last action results
            - step_count: Number of steps taken
        verifier_results: Verification results for each branch

    Returns:
        Index of the selected branch (0-indexed)
    """
    # If only one branch or one succeeded, return early
    if len(branches) == 1:
        return 0

    # If any branch succeeded, return it immediately
    for i, (success, _) in enumerate(verifier_results):
        if success:
            return i

    # Build evaluation prompt
    prompt = f"""You are evaluating different strategies for a multi-agent cooperative game task.

{task_context}

## Branches to Evaluate

"""

    for i, branch in enumerate(branches):
        prompt += format_branch_for_prompt(
            i,
            branch.get('agent_states', {}),
            branch.get('last_actions', {}),
            verifier_results[i]
        )
        prompt += "\n\n"

    prompt += """
## Your Task

Analyze these branches and select the one most likely to succeed in completing the task objective.

Consider:
1. Progress toward the goal (do agents have needed items?)
2. Positioning (are agents in good locations?)
3. Resource collection status
4. Coordination between agents
5. Whether last actions moved toward or away from the goal

Respond with ONLY a JSON object containing:
- "selected_branch": the branch number (1 or 2)
- "reasoning": brief explanation (1-2 sentences)

Example:
```json
{"selected_branch": 1, "reasoning": "Branch 1 has collected more resources and agents are closer to completing the craft."}
```

Your selection:
"""

    # Call Claude
    response = call_claude(prompt)

    # Parse response
    selected = parse_branch_selection(response, len(branches))

    return selected


def parse_branch_selection(response: str, num_branches: int) -> int:
    """
    Parse Claude's response to extract selected branch index.

    Args:
        response: Claude's response string
        num_branches: Number of branches to select from

    Returns:
        Selected branch index (0-indexed)
    """
    # Try to find JSON in response
    json_match = re.search(r'\{[^{}]*"selected_branch"[^{}]*\}', response, re.DOTALL)

    if json_match:
        try:
            data = json.loads(json_match.group())
            selected = data.get('selected_branch', 1)
            # Convert to 0-indexed
            if isinstance(selected, int) and 1 <= selected <= num_branches:
                return selected - 1
        except json.JSONDecodeError:
            pass

    # Try to find a number
    number_match = re.search(r'(?:branch|select|choose)\s*[:#]?\s*(\d+)', response.lower())
    if number_match:
        selected = int(number_match.group(1))
        if 1 <= selected <= num_branches:
            return selected - 1

    # Default to first branch
    return 0


def score_branch(
    branch: Dict[str, Any],
    task_context: str,
    verifier_result: Tuple[bool, str]
) -> float:
    """
    Calculate a simple heuristic score for a branch.

    This can be used as a fallback when Claude is not available.

    Args:
        branch: Branch state
        task_context: Task description
        verifier_result: Verification result

    Returns:
        Score (higher is better)
    """
    score = 0.0

    # Success is best
    if verifier_result[0]:
        return 1000.0

    agent_states = branch.get('agent_states', {})

    # Score based on inventory items collected
    for agent_name, state in agent_states.items():
        for item in state.get('inventory', []):
            if item and item.get('key'):
                # More items is generally better for crafting tasks
                score += item.get('count', 1) * 2

        # Score based on equipment
        for slot, item in state.get('equipment', {}).items():
            if item and item.get('key'):
                score += 5

        # Penalize dead agents
        if state.get('dead', False) or state.get('hitPoints', 0) <= 0:
            score -= 100

    # Score based on successful actions
    last_actions = branch.get('last_actions', {})
    for agent_name, action_result in last_actions.items():
        if action_result.get('success', False):
            score += 1

    return score


def select_best_branches(
    branches: List[Dict[str, Any]],
    verifier_results: List[Tuple[bool, str]],
    task_context: str,
    max_branches: int = 2,
    use_claude: bool = True
) -> List[int]:
    """
    Select the best branches to keep for next iteration.

    Args:
        branches: All current branches
        verifier_results: Verification results for each branch
        task_context: Task description
        max_branches: Maximum number of branches to keep
        use_claude: Whether to use Claude for evaluation

    Returns:
        List of branch indices to keep
    """
    # If any succeeded, return only successful ones
    successful = [i for i, (success, _) in enumerate(verifier_results) if success]
    if successful:
        return successful[:max_branches]

    # If only a few branches, keep all
    if len(branches) <= max_branches:
        return list(range(len(branches)))

    if use_claude and len(branches) > 1:
        # Use Claude to select the best one
        try:
            best = evaluate_branches(task_context, branches, verifier_results)
            # Keep the best and the next best by score
            scores = [(i, score_branch(b, task_context, verifier_results[i]))
                      for i, b in enumerate(branches)]
            scores.sort(key=lambda x: x[1], reverse=True)

            result = [best]
            for i, _ in scores:
                if i != best and len(result) < max_branches:
                    result.append(i)
            return result
        except Exception:
            pass

    # Fallback: use heuristic scoring
    scores = [(i, score_branch(b, task_context, verifier_results[i]))
              for i, b in enumerate(branches)]
    scores.sort(key=lambda x: x[1], reverse=True)

    return [i for i, _ in scores[:max_branches]]


if __name__ == '__main__':
    # Test the module
    print("Testing branch evaluator...")

    # Create test branches
    test_branches = [
        {
            'agent_states': {
                'lumberjack': {'x': 387, 'y': 3, 'hitPoints': 100, 'maxHitPoints': 100,
                               'inventory': [{'key': 'logs', 'count': 2}], 'equipment': {}, 'dead': False},
                'wizard': {'x': 392, 'y': 3, 'hitPoints': 100, 'maxHitPoints': 100,
                           'inventory': [{'key': 'bead', 'count': 1}], 'equipment': {}, 'dead': False}
            },
            'last_actions': {
                'lumberjack': {'action': {'type': 'collect'}, 'success': True, 'message': 'Collected logs'},
                'wizard': {'action': {'type': 'wait'}, 'success': True, 'message': 'Waiting'}
            },
            'step_count': 1
        },
        {
            'agent_states': {
                'lumberjack': {'x': 388, 'y': 3, 'hitPoints': 100, 'maxHitPoints': 100,
                               'inventory': [], 'equipment': {}, 'dead': False},
                'wizard': {'x': 391, 'y': 3, 'hitPoints': 100, 'maxHitPoints': 100,
                           'inventory': [{'key': 'bead', 'count': 1}], 'equipment': {}, 'dead': False}
            },
            'last_actions': {
                'lumberjack': {'action': {'type': 'move'}, 'success': True, 'message': 'Moved'},
                'wizard': {'action': {'type': 'move'}, 'success': True, 'message': 'Moved'}
            },
            'step_count': 1
        }
    ]

    test_results = [(False, 'Task incomplete'), (False, 'Task incomplete')]

    # Test scoring
    for i, branch in enumerate(test_branches):
        score = score_branch(branch, "Craft a staff", test_results[i])
        print(f"Branch {i+1} score: {score}")

    # Test selection without Claude
    selected = select_best_branches(test_branches, test_results, "Craft a staff", max_branches=1, use_claude=False)
    print(f"Selected branches (heuristic): {selected}")
