#!/usr/bin/env python3
"""
CCE v2: Proper backward causal tracing.

Step 1: Identify success actions from the last rounds
Step 2: Backward trace round-by-round, asking LLM per round:
        "Which actions in this round enable any of the current green set?"
Step 3: Compute CE and PAC

Usage:
    python scripts/compute_cce_v2.py --model gemini --task 1 --verbose
"""

import json
import glob
import os
import re
import argparse
from openai import OpenAI

# Config
API_KEY = os.environ["DIGITALOCEAN_TOKEN"]
BASE_URL = "https://inference.do-ai.run/v1"
JUDGE_MODEL = "nvidia-nemotron-3-super-120b"

MODEL_DIRS = {
    'gemini': 'gemini_v1.3',
    'claude': 'claude_haiku45_v1.3',
    'gpt5': 'gpt5mini_b2_original',
    'deepseek': 'deepseek_b2_original',
    'gpt5_aug': 'gpt5mini_augmented',
    'claude_aug': 'claude_haiku45_augmented',
    'deepseek_aug': 'deepseek_augmented',
    'gemini_aug': 'gemini_augmented',
}
LOGS_BASE = os.path.expanduser('~/works/agentworld/agents/logs')

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_llm(prompt, verbose=False):
    """Call LLM and parse JSON response."""
    if verbose:
        print(f"\n{'─'*60}")
        print(f"PROMPT ({len(prompt)} chars):")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print(f"{'─'*60}")

    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        max_tokens=8192,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()

    if verbose:
        print(f"RESPONSE: {text[:300]}")

    # Parse JSON
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```\s*$', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try extracting JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        # Try extracting array from key
        match = re.search(r'"(?:contributing|success)[^"]*"\s*:\s*\[([\d\s,]*)', text)
        if match:
            ids = [int(x) for x in re.findall(r'\d+', match.group(1))]
            return {"ids": ids}
        print(f"  WARNING: Could not parse: {text[:150]}")
        return None


def extract_actions(trajectory):
    """Extract all actions as list of dicts."""
    actions = []
    for r in trajectory.get('rounds', []):
        for a in r.get('actions', []):
            action_str = a.get('action', '').strip()
            if action_str:
                actions.append({
                    'round': r['round'],
                    'agent': a['agent_name'],
                    'action': action_str,
                })
    return actions


def format_action(idx, action):
    """Format a single action for display."""
    return f"[{idx}] Round {action['round']}, {action['agent']}: {action['action'][:150]}"


def step1_identify_success_actions(actions, task_def, verification_msg, verbose=False):
    """Step 1: Identify which actions directly achieved the success criteria."""
    task_name = task_def.get('task', {}).get('name', 'Unknown')
    objective = task_def.get('objectives', {}).get('primary', 'Unknown')

    # Format all actions
    actions_text = '\n'.join(format_action(i, a) for i, a in enumerate(actions))

    prompt = f"""You are analyzing a multi-agent collaboration task.

TASK: {task_name}
OBJECTIVE: {objective}

ALL ACTIONS IN THE TRAJECTORY:
{actions_text}

QUESTION: Which actions are the FINAL actions that directly accomplished the objective? These are the terminal actions whose completion means the objective is achieved (e.g., the craft action that produced the target item, the kill action that defeated the target boss).

Do NOT include any enabling or prerequisite actions (gathering materials, moving, chatting, transferring items). Only the very last action(s) that fulfill the objective.

Respond with JSON:
{{"success_action_ids": [list of action indices], "reasoning": "brief explanation"}}"""

    result = call_llm(prompt, verbose=verbose)
    if result:
        return result.get('success_action_ids', result.get('ids', []))
    return []


def step2_trace_round(round_num, round_actions, round_action_indices, green_set, actions, task_objective, game_context="", verbose=False):
    """Step 2: For a given round, ask which actions enable any green actions."""
    if not round_actions:
        return []

    # Format the actions in this round
    round_text = '\n'.join(
        f"[{idx}] {actions[idx]['agent']}: {actions[idx]['action'][:150]}"
        for idx in round_action_indices
    )

    # Format the current green set (actions from strictly LATER rounds that contribute to success)
    # Actions in the same round are simultaneous and cannot causally enable each other
    green_relevant = [(i, actions[i]) for i in sorted(green_set) if actions[i]['round'] > round_num]
    if not green_relevant:
        # If no green actions in later rounds, these round actions can't enable anything
        return []

    green_text = '\n'.join(
        f"  - [{i}] Round {a['round']}, {a['agent']}: {a['action'][:120]}"
        for i, a in green_relevant[:30]  # Limit to avoid huge prompts
    )

    # Include game context if available (crafting recipes, resource dependencies)
    context_section = ""
    if game_context:
        context_section = f"\nGAME CONTEXT (crafting recipes and resource dependencies):\n{game_context}\n"

    prompt = f"""You are tracing causal dependencies in a multi-agent collaboration task.

TASK OBJECTIVE: {task_objective}
{context_section}
The following actions from LATER rounds have been identified as contributing to the task's success:
{green_text}

Now consider the actions from Round {round_num}:
{round_text}

QUESTION: For each action in Round {round_num}, does it causally ENABLE or CONTRIBUTE TO any of the contributing actions listed above?

An action contributes if:
- It produces resources/items that a later contributing action uses (check crafting recipes above)
- It transfers items to an agent who later uses them in a contributing action
- It moves the agent to a location needed for a later contributing action
- It communicates information that helps coordinate a later contributing action
- It is a prerequisite step (e.g., harvesting before transferring, transferring before crafting)

Be INCLUSIVE: if an action is even somewhat helpful, mark it as contributing.

An action does NOT contribute if:
- It is completely unrelated to any contributing action (e.g., sleeping, wandering)
- Its effects are never used by any later contributing action

Respond with JSON:
{{"contributing_ids": [list of action indices from Round {round_num} that contribute], "not_contributing_ids": [remaining indices]}}"""

    result = call_llm(prompt, verbose=verbose)
    if result:
        return result.get('contributing_ids', result.get('ids', []))
    return []


def compute_cce_v2(trajectory, verbose=False):
    """Compute CCE using proper backward causal tracing."""
    task_id = trajectory.get('task_id', 'unknown')
    metrics = trajectory.get('metrics', {})
    success = metrics.get('task_verified_success', False)
    verification_msg = metrics.get('task_verification_message', '')
    task_def = trajectory.get('task_definition', {})
    objective = task_def.get('objectives', {}).get('primary', 'Unknown')
    # Extract just the crafting recipes / resource dependency section (not the full context)
    full_context = task_def.get('relevant_game_context', '')
    # Try to extract from CRAFTING RECIPES section onwards, or ITEM KEY section
    game_context = full_context
    for marker in ['CRAFTING RECIPES', 'ITEM KEY REFERENCE', 'RECIPE', 'STRATEGY']:
        idx = full_context.find(marker)
        if idx != -1:
            game_context = full_context[idx:]
            break
    # Truncate to avoid token limits
    if len(game_context) > 1500:
        game_context = game_context[:1500] + '\n...'

    actions = extract_actions(trajectory)
    agents = sorted(set(a['agent'] for a in actions))

    if not success:
        return {
            'task_id': task_id, 'success': False,
            'ce': 0.0, 'total_actions': len(actions),
            'contributing_actions': 0,
            'pac': {a: 0.0 for a in agents},
            'green_set': [],
        }

    if not actions:
        return {
            'task_id': task_id, 'success': True,
            'ce': 0.0, 'total_actions': 0,
            'contributing_actions': 0, 'pac': {},
            'green_set': [],
        }

    # Group actions by round
    rounds = {}
    for i, a in enumerate(actions):
        r = a['round']
        if r not in rounds:
            rounds[r] = []
        rounds[r].append(i)

    max_round = max(rounds.keys())
    min_round = min(rounds.keys())

    # Step 1: Identify success actions
    if verbose:
        print(f"\n{'='*60}")
        print(f"STEP 1: Identify success actions")
        print(f"{'='*60}")

    success_ids = step1_identify_success_actions(actions, task_def, verification_msg, verbose=verbose)
    green_set = set(success_ids)

    if verbose:
        print(f"\nSuccess actions: {sorted(green_set)}")
        for idx in sorted(green_set):
            if idx < len(actions):
                print(f"  {format_action(idx, actions[idx])}")

    # Step 2: Backward trace round by round
    if verbose:
        print(f"\n{'='*60}")
        print(f"STEP 2: Backward tracing (rounds {max_round} → {min_round})")
        print(f"{'='*60}")

    for r in range(max_round, min_round - 1, -1):
        if r not in rounds:
            continue

        round_indices = rounds[r]
        # Skip actions already in green set
        candidates = [i for i in round_indices if i not in green_set]

        if not candidates:
            if verbose:
                print(f"\n  Round {r}: all {len(round_indices)} actions already in green set, skip")
            continue

        # Check if there are any green actions in strictly later rounds to trace back to
        green_relevant = [i for i in green_set if actions[i]['round'] > r]
        if not green_relevant:
            if verbose:
                print(f"\n  Round {r}: no green actions to trace back to, skip")
            continue

        if verbose:
            print(f"\n  Round {r}: {len(candidates)} candidate actions, {len(green_relevant)} green targets")

        new_contributing = step2_trace_round(
            r, [actions[i] for i in candidates], candidates,
            green_set, actions, objective, game_context=game_context, verbose=verbose
        )

        if new_contributing:
            green_set.update(new_contributing)
            if verbose:
                print(f"  → Added {len(new_contributing)} actions: {new_contributing}")
                for idx in new_contributing:
                    if idx < len(actions):
                        print(f"    {format_action(idx, actions[idx])}")

    # Step 3: Compute metrics
    total = len(actions)
    contributing = len(green_set)
    ce = contributing / total if total > 0 else 0.0

    pac = {}
    for agent in agents:
        agent_total = sum(1 for a in actions if a['agent'] == agent)
        agent_green = sum(1 for i in green_set if i < len(actions) and actions[i]['agent'] == agent)
        pac[agent] = round(agent_green / agent_total, 4) if agent_total > 0 else 0.0

    return {
        'task_id': task_id,
        'success': True,
        'ce': round(ce, 4),
        'total_actions': total,
        'contributing_actions': contributing,
        'pac': pac,
        'green_set': sorted(green_set),
        'num_rounds': max_round,
        'llm_calls': max_round - min_round + 2,  # +1 for step1, +1 for inclusive
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='gemini', choices=MODEL_DIRS.keys())
    parser.add_argument('--task', type=str, default='1', help='Task number or "all" for batch run')
    parser.add_argument('--verbose', action='store_true', help='Print detailed LLM interactions')
    parser.add_argument('--output', type=str, default=None, help='Output JSON file')
    args = parser.parse_args()

    model_dir = os.path.join(LOGS_BASE, MODEL_DIRS[args.model])

    # Determine task list
    if args.task == 'all':
        traj_files = sorted(glob.glob(os.path.join(model_dir, 'task_*_trajectory.json')))
        tasks = []
        for f in traj_files:
            m = re.search(r'task_(\d+)', os.path.basename(f))
            if m:
                tasks.append((int(m.group(1)), f))
    else:
        task_num = int(args.task)
        filepath = os.path.join(model_dir, f'task_{task_num:02d}_trajectory.json')
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return
        tasks = [(task_num, filepath)]

    print(f"CCE v2 | Model: {args.model} | Judge: {JUDGE_MODEL} | Tasks: {len(tasks)}")
    print(f"{'='*70}")

    all_results = []
    for task_num, filepath in tasks:
        trajectory = json.load(open(filepath))
        task_id = trajectory.get('task_id', f'task_{task_num:02d}')
        success = trajectory.get('metrics', {}).get('task_verified_success', False)

        print(f"\nTask {task_num:3d}: ", end='', flush=True)

        if not success:
            result = compute_cce_v2(trajectory, verbose=args.verbose)
            print(f"FAILED (CE=0.0)")
        else:
            try:
                result = compute_cce_v2(trajectory, verbose=args.verbose)
                print(f"SUCCESS | CE={result['ce']:.3f} ({result['contributing_actions']}/{result['total_actions']})")
            except Exception as e:
                print(f"ERROR: {e}")
                result = {'task_id': task_id, 'success': True, 'ce': None, 'error': str(e)}

        all_results.append(result)

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    successful = [r for r in all_results if r.get('success') and r.get('ce') is not None]
    failed = [r for r in all_results if not r.get('success')]
    errors = [r for r in all_results if r.get('error')]

    print(f"Total: {len(all_results)} | Success: {len(successful)} | Failed: {len(failed)} | Errors: {len(errors)}")

    if successful:
        avg_ce_success = sum(r['ce'] for r in successful) / len(successful)
        print(f"Avg CE (successful only): {avg_ce_success:.4f}")

    all_ce = [r['ce'] for r in all_results if r.get('ce') is not None]
    if all_ce:
        avg_ce_all = sum(all_ce) / len(all_ce)
        print(f"Avg CE (all tasks):       {avg_ce_all:.4f}")

    # Save results
    output_path = args.output or f'results/cce_v2_{args.model}_{JUDGE_MODEL}.json'
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            'model': args.model,
            'judge': JUDGE_MODEL,
            'results': all_results,
            'summary': {
                'total': len(all_results),
                'successful': len(successful),
                'failed': len(failed),
                'avg_ce_successful': round(avg_ce_success, 4) if successful else None,
                'avg_ce_all': round(avg_ce_all, 4) if all_ce else None,
            }
        }, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == '__main__':
    main()
