#!/usr/bin/env python3
"""
Compute Causal Collaboration Effectiveness (CCE) for AgentWorld trajectories.

For each successful task trajectory:
1. Extract all actions as (round, agent, action) tuples
2. Send to LLM with task context, ask which actions causally contributed to success
3. Compute CE = |contributing| / |total|
4. Compute PAC_i = |contributing ∩ agent_i| / |agent_i| for each agent

For failed tasks: CE = 0 by definition.

Usage:
    python scripts/compute_cce.py --model gemini --tasks 1-10
    python scripts/compute_cce.py --model gemini --tasks all --limit 20
"""

import json
import glob
import os
import sys
import argparse
import re
from pathlib import Path

# Model dirs
MODEL_DIRS = {
    'gemini': 'gemini_v1.3',
    'claude': 'claude_haiku45_v1.3',
    'gpt5': 'gpt5mini_b2_original',
    'deepseek': 'deepseek_b2_original',
}

LOGS_BASE = os.path.expanduser('~/works/agentworld/agents/logs')


def load_trajectory(filepath):
    """Load and parse a trajectory JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    return data


def extract_actions(trajectory):
    """Extract all actions as a list of dicts with round, agent, action."""
    actions = []
    for r in trajectory.get('rounds', []):
        round_num = r['round']
        for a in r.get('actions', []):
            action_str = a.get('action', '').strip()
            if action_str:
                actions.append({
                    'id': f"R{round_num}_{a['agent_name']}",
                    'round': round_num,
                    'agent': a['agent_name'],
                    'action': action_str,
                })
    return actions


def format_actions_for_llm(actions):
    """Format actions into a numbered list for the LLM prompt."""
    lines = []
    for i, a in enumerate(actions):
        # Truncate very long actions
        action_text = a['action'][:200]
        lines.append(f"[{i}] Round {a['round']}, {a['agent']}: {action_text}")
    return '\n'.join(lines)


def build_cce_prompt(task_def, actions, verification_msg):
    """Build the prompt for the LLM to identify contributing actions."""
    task_name = task_def.get('task', {}).get('name', 'Unknown')
    objective = task_def.get('objectives', {}).get('primary', 'Unknown')
    success_criteria = task_def.get('success_criteria', [])

    actions_text = format_actions_for_llm(actions)
    num_actions = len(actions)

    prompt = f"""You are analyzing a multi-agent collaboration task to determine which actions causally contributed to the task's success.

TASK: {task_name}
OBJECTIVE: {objective}
SUCCESS CRITERIA: {json.dumps(success_criteria)}
VERIFICATION RESULT: {verification_msg}

The following is the complete list of actions taken by all agents during the task. Each action is numbered [0] through [{num_actions - 1}].

ACTIONS:
{actions_text}

INSTRUCTIONS:
For each action, determine whether it CAUSALLY CONTRIBUTED to the task's success. An action is contributing if:
- It directly achieved part of the success criteria, OR
- It enabled or was necessary for another contributing action (e.g., gathering materials that were later used in crafting)
- Communication that coordinated contributing actions counts as contributing

Be INCLUSIVE: if an action is even somewhat helpful to the final outcome, mark it as contributing. It is better to include a marginally helpful action than to miss a genuinely contributing one.

An action is NOT contributing if:
- It had no effect on the outcome (e.g., sleeping, waiting, moving to irrelevant locations)
- It was redundant (e.g., gathering resources that were never used)

Respond with a JSON object:
{{
  "contributing_ids": [list of action indices that contributed, e.g. [0, 1, 3, 5]],
  "reasoning": "brief explanation of the causal chain"
}}

Only output the JSON object, nothing else."""

    return prompt


def call_llm(prompt, model="gemini"):
    """Call LLM API to get contributing action IDs."""
    from openai import OpenAI

    # Use the OpenAI-compatible proxy
    API_KEY = "sk-QJ3tm90vbicqSOMEW5auku5OeR6cvbHo59yy7mRNH5hxCuTz"
    BASE_URL = "https://yinli.one/v1"

    model_map = {
        "gemini": "gemini-2.5-flash",
        "claude": "anthropic-claude-haiku-4.5",
        "gpt5": "gpt-5",
        "gpt5mini": "openai-gpt-5-mini",
    }

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=model_map.get(model, model),
        max_tokens=2000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content

    # Parse JSON from response
    try:
        text = text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```\s*$', '', text)
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object from the text
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass

    # Try to extract just the contributing_ids array (handles truncated/malformed JSON)
    try:
        match = re.search(r'"contributing_ids"\s*:\s*\[([\d\s,]*)', text, re.DOTALL)
        if match:
            raw = match.group(1)
            # Extract all integers
            ids = [int(x) for x in re.findall(r'\d+', raw)]
            reasoning = ""
            rmatch = re.search(r'"reasoning"\s*:\s*"([^"]*)', text, re.DOTALL)
            if rmatch:
                reasoning = rmatch.group(1)
            return {"contributing_ids": ids, "reasoning": reasoning or "parsed from partial response"}
    except:
        pass

    print(f"  WARNING: Could not parse LLM response: {text[:150]}...")
    return None


def compute_cce(trajectory, llm_model="gemini"):
    """Compute CCE for a single trajectory."""
    task_id = trajectory.get('task_id', 'unknown')
    metrics = trajectory.get('metrics', {})
    success = metrics.get('task_verified_success', False)
    verification_msg = metrics.get('task_verification_message', '')

    # For failed tasks, CE = 0
    if not success:
        actions = extract_actions(trajectory)
        agents = set(a['agent'] for a in actions)
        return {
            'task_id': task_id,
            'success': False,
            'ce': 0.0,
            'total_actions': len(actions),
            'contributing_actions': 0,
            'pac': {agent: 0.0 for agent in agents},
            'reasoning': 'Task failed, CE=0 by definition',
        }

    # Extract actions
    actions = extract_actions(trajectory)
    if not actions:
        return {
            'task_id': task_id,
            'success': True,
            'ce': 0.0,
            'total_actions': 0,
            'contributing_actions': 0,
            'pac': {},
            'reasoning': 'No actions found',
        }

    # Build prompt and call LLM
    task_def = trajectory.get('task_definition', {})
    prompt = build_cce_prompt(task_def, actions, verification_msg)
    result = call_llm(prompt, model=llm_model)

    if result is None:
        return {
            'task_id': task_id,
            'success': True,
            'ce': None,
            'total_actions': len(actions),
            'contributing_actions': None,
            'pac': {},
            'reasoning': 'LLM call failed',
        }

    contributing_ids = set(result.get('contributing_ids', []))
    reasoning = result.get('reasoning', '')

    # Compute metrics
    total = len(actions)
    contributing = len(contributing_ids)
    ce = contributing / total if total > 0 else 0.0

    # Per-agent contribution
    agents = {}
    for i, a in enumerate(actions):
        agent = a['agent']
        if agent not in agents:
            agents[agent] = {'total': 0, 'contributing': 0}
        agents[agent]['total'] += 1
        if i in contributing_ids:
            agents[agent]['contributing'] += 1

    pac = {}
    for agent, counts in agents.items():
        pac[agent] = counts['contributing'] / counts['total'] if counts['total'] > 0 else 0.0

    return {
        'task_id': task_id,
        'success': True,
        'ce': round(ce, 4),
        'total_actions': total,
        'contributing_actions': contributing,
        'pac': {k: round(v, 4) for k, v in pac.items()},
        'contributing_ids': sorted(contributing_ids),
        'reasoning': reasoning,
    }


def main():
    parser = argparse.ArgumentParser(description='Compute CCE for AgentWorld trajectories')
    parser.add_argument('--model', type=str, default='gemini', choices=MODEL_DIRS.keys(),
                        help='Agent model to evaluate')
    parser.add_argument('--tasks', type=str, default='1-5',
                        help='Task range (e.g., "1-10", "all", "1,3,5")')
    parser.add_argument('--limit', type=int, default=None,
                        help='Max number of tasks to process')
    parser.add_argument('--llm', type=str, default='gemini',
                        choices=['gemini', 'claude'],
                        help='LLM to use as judge')
    parser.add_argument('--output', type=str, default=None,
                        help='Output JSON file path')
    args = parser.parse_args()

    # Find trajectory files
    model_dir = os.path.join(LOGS_BASE, MODEL_DIRS[args.model])
    traj_files = sorted(glob.glob(os.path.join(model_dir, 'task_*_trajectory.json')))

    # Parse task range
    if args.tasks == 'all':
        task_nums = None  # process all
    elif '-' in args.tasks:
        lo, hi = args.tasks.split('-')
        task_nums = set(range(int(lo), int(hi) + 1))
    elif ',' in args.tasks:
        task_nums = set(int(x) for x in args.tasks.split(','))
    else:
        task_nums = {int(args.tasks)}

    # Filter files
    selected = []
    for f in traj_files:
        match = re.search(r'task_(\d+)', os.path.basename(f))
        if match:
            num = int(match.group(1))
            if task_nums is None or num in task_nums:
                selected.append((num, f))

    if args.limit:
        selected = selected[:args.limit]

    print(f"Computing CCE for {len(selected)} tasks using {args.model} trajectories, judged by {args.llm}")
    print(f"{'='*70}")

    results = []
    for task_num, filepath in selected:
        print(f"\nTask {task_num:3d}: ", end='', flush=True)
        trajectory = load_trajectory(filepath)
        success = trajectory.get('metrics', {}).get('task_verified_success', False)

        if not success:
            print(f"FAILED (CE=0.0)")
            result = compute_cce(trajectory, llm_model=args.llm)
        else:
            result = compute_cce(trajectory, llm_model=args.llm)
            if result['ce'] is not None:
                print(f"SUCCESS | CE={result['ce']:.2f} | {result['contributing_actions']}/{result['total_actions']} actions")
                for agent, pac in result['pac'].items():
                    agent_short = agent.split('_')[0] if '_' in agent else agent
                    print(f"         PAC({agent_short})={pac:.2f}", end='')
                print()
            else:
                print(f"SUCCESS | CE=ERROR (LLM call failed)")

        results.append(result)

    # Summary
    print(f"\n{'='*70}")
    successful = [r for r in results if r['success'] and r['ce'] is not None]
    failed = [r for r in results if not r['success']]
    print(f"Total tasks: {len(results)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")

    all_ce = [r['ce'] for r in results if r['ce'] is not None]
    avg_ce = sum(r['ce'] for r in successful) / len(successful) if successful else 0
    overall_ce = sum(all_ce) / len(all_ce) if all_ce else 0

    if successful:
        print(f"\n  Avg CE (successful only): {avg_ce:.4f}")
    print(f"  Avg CE (all tasks):       {overall_ce:.4f}")

    # Save results
    output_path = args.output or f'results/cce_{args.model}_{args.llm}_judge.json'
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            'model': args.model,
            'llm_judge': args.llm,
            'task_range': args.tasks,
            'results': results,
            'summary': {
                'total_tasks': len(results),
                'successful_tasks': len(successful),
                'failed_tasks': len(failed),
                'avg_ce_successful': round(avg_ce, 4) if successful else None,
                'avg_ce_all': round(overall_ce, 4) if all_ce else None,
            }
        }, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
