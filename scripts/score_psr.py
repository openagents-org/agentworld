#!/usr/bin/env python3
"""Reconstruct checkpoint PSR from agentworld_paper/colm/main.tex:286.

Numeric quantity checkpoints receive min(actual / required, 1); booleans
receive 0/1. Round limits are boolean upper-bound checks, not quantities to
accumulate. Checkpoints have equal weight within a task, tasks equal weight
within a set, and successful tasks receive 1. This explicit reconstruction
has not been cross-validated against the unavailable historical PSR program.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
METHOD = 'checkpoint_fraction_v1'
DEFINITION = ('Mean checkpoint completion per task, then mean across tasks; '
              'quantities clipped actual/required, booleans 0/1, round-limit '
              'checks actual<=limit, successful tasks forced to 1.')

# Denominators omitted from messages, read from task_verifier.py predicates.
BARE_TARGETS = {
    ('07', 'Pickaxe count'): 1,
    ('31', 'Sticks'): 10, ('31', 'Logs'): 5,
    ('52', 'Weapons crafted'): 2,
    ('57', 'Gems'): 5, ('57', 'Jewelry'): 2,
    ('60', 'Ores'): 15, ('60', 'Bars'): 5,
    ('65', 'Potions/consumables'): 5,
}


def checkpoint_score(task, message, success):
    if success:
        return {'PSR': 1.0, 'successful_task_override': True, 'checkpoints': []}
    number = re.match(r'task_(\d+)_', task).group(1)
    checkpoints = []
    for part in message.split(','):
        label, value = (s.strip() for s in part.split(':', 1))
        if value in ('True', 'False'):
            credit = float(value == 'True')
            details = {'kind': 'boolean', 'actual': value == 'True'}
        else:
            match = re.fullmatch(r'(\d+(?:\.\d+)?)(?:/(\d+(?:\.\d+)?))?', value)
            if not match:
                raise ValueError(f'Unrecognized checkpoint: {task}: {part}')
            actual = float(match.group(1))
            target = float(match.group(2)) if match.group(2) else BARE_TARGETS[(number, label)]
            if target <= 0:
                raise ValueError(f'Invalid target: {task}: {part}')
            if label == 'Rounds':
                credit = float(actual <= target)
                kind = 'upper_bound'
            else:
                credit = min(actual / target, 1.0)
                kind = 'quantity'
            details = {'kind': kind, 'actual': actual, 'target': target}
        checkpoints.append({'label': label, **details, 'credit': credit})
    if not checkpoints:
        raise ValueError(f'No checkpoints: {task}')
    return {'PSR': sum(c['credit'] for c in checkpoints) / len(checkpoints),
            'successful_task_override': False, 'checkpoints': checkpoints}


def expected_task_sets(root=ROOT):
    """Use task identities, not just counts, to establish completeness."""
    return {stage: {p.stem for p in (root / 'data_v0.1_multi' / dataset).glob('*.yaml')}
            for stage, dataset in [('main', 'v1.3_benchmark'),
                                   ('augmented', 'v1.3_augmented')]}


def calculate(inputs, expected_tasks=None):
    expected_tasks = expected_task_sets() if expected_tasks is None else expected_tasks
    if not all(expected_tasks.get(stage) for stage in ('main', 'augmented')):
        raise ValueError('Expected benchmark YAML task sets are missing')
    results = {}
    for model, rows in inputs.items():
        seen = set()
        for row in rows:
            identity = (row['stage'], row['task'])
            if identity in seen:
                raise ValueError(f'Duplicate task: {model}/{identity}')
            seen.add(identity)
            if row['task'] not in expected_tasks.get(row['stage'], set()):
                raise ValueError(f'Unexpected task: {model}/{identity}')
            if type(row['success']) is not bool:
                raise ValueError(f'Success must be boolean: {model}/{identity}')
            for key in ('CCE', 'rounds', 'chats'):
                value = row[key]
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    raise ValueError(f'Invalid {key}: {model}/{identity}')
            if row['CCE'] > 1 or (not row['success'] and row['CCE'] != 0):
                raise ValueError(f'Invalid CCE for task outcome: {model}/{identity}')
        scored = [{**row, **checkpoint_score(row['task'], row['message'], row['success'])}
                  for row in rows]
        summaries = {}
        for subset in ['main', 'augmented_v1', 'augmented_v2', 'augmented']:
            selected = [r for r in scored if
                        (r['stage'] == 'main' if subset == 'main' else
                         r['stage'] == 'augmented' and
                         (subset == 'augmented' or r['task'].endswith('_' + subset[-2:]))) ]
            n = len(selected)
            expected_ids = expected_tasks['main' if subset == 'main' else 'augmented']
            if subset in ('augmented_v1', 'augmented_v2'):
                expected_ids = {t for t in expected_ids if t.endswith('_' + subset[-2:])}
            expected = len(expected_ids)
            summaries[subset] = {
                'scored': n, 'expected': expected,
                'final': {r['task'] for r in selected} == expected_ids,
                'missing_tasks': sorted(expected_ids - {r['task'] for r in selected}),
                **({key: sum(row[source] for row in selected) / n * scale
                    for key, source, scale in [('SR_percent', 'success', 100),
                        ('PSR_percent', 'PSR', 100), ('CCE', 'CCE', 1),
                        ('rounds', 'rounds', 1), ('chats', 'chats', 1)]} if n else {})}
        results[model] = {'summary': summaries, 'tasks': scored}
    return {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'method': METHOD, 'definition': DEFINITION,
            'source': 'agentworld_paper/colm/main.tex:286',
            'historical_implementation_reproduced': False, 'models': results}


def collect(root, previous, results_root=None):
    """Collect completed/CCE-scored attempts; initialization must be audited first."""
    sys.path.insert(0, str(root))
    from task_verifier import verify_task
    verifier_hash = hashlib.sha256((root / 'task_verifier.py').read_bytes()).hexdigest()
    inputs = {}
    results_root = results_root or root / 'agents/logs/additional_20260925'
    folders = sorted(p for p in results_root.iterdir()
                     if p.is_dir() and any((p / s).is_dir() for s in ('main', 'augmented')))
    if not folders:
        raise ValueError(f'No model result folders found in {results_root}')
    for model_folder in folders:
        model = model_folder.name
        cached = {(row['stage'], row['task']): row for row in previous.get(model, [])}
        rows = []
        for stage in ['main', 'augmented']:
            folder = model_folder / stage
            for marker in sorted(folder.glob('*/completed.json')):
                cce_file = marker.parent / 'cce.json'
                if not cce_file.exists():
                    continue
                completed_text, cce_text = marker.read_text(), cce_file.read_text()
                completed, cce = json.loads(completed_text), json.loads(cce_text)
                saved_path = Path(completed['trajectory'])
                # Prefer the sibling attempt after moving/copying result folders.
                local_path = marker.parent / saved_path.parent.name / saved_path.name
                trajectory_path = local_path if local_path.is_file() else saved_path
                trajectory_text = trajectory_path.read_text()
                trajectory = json.loads(trajectory_text)
                if (completed['task'] != marker.parent.name or
                        Path(trajectory['task_source']).stem != completed['task'] or
                        Path(cce['task_source']).stem != completed['task']):
                    raise ValueError(f'Task identity mismatch: {marker}')
                if completed['metrics'] != trajectory['metrics']:
                    raise ValueError(f'Marker/trajectory metrics mismatch: {marker}')
                if (trajectory_path.parent / 'infra_error.txt').exists():
                    raise ValueError(f'Infrastructure failure marked complete: {marker}')
                fingerprint = hashlib.sha256((completed_text + cce_text + verifier_hash
                                              + trajectory_text).encode()).hexdigest()
                old = cached.get((stage, completed['task']))
                if old and old.get('_fingerprint') == fingerprint:
                    rows.append(old)
                    continue
                version = 1 if completed['task'].endswith('_v1') else 2 if completed['task'].endswith('_v2') else 0
                passed, message = verify_task(trajectory, version=version)
                if bool(passed) != cce['success']:
                    raise ValueError(f"Verifier/CCE success mismatch: {model}/{completed['task']}")
                rows.append({'stage': stage, 'task': completed['task'],
                             'success': bool(passed), 'message': message,
                             'CCE': cce['ce'], 'rounds': completed['metrics']['total_rounds'],
                             'chats': completed['metrics']['total_chats'],
                             '_fingerprint': fingerprint})
        inputs[model] = rows
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--collect-root', type=Path,
                        help='Repository containing task_verifier.py and benchmark YAMLs')
    parser.add_argument('--results-root', type=Path,
                        help='Collect MODEL/{main,augmented}/TASK/completed.json from this directory')
    args = parser.parse_args()
    if args.inputs.resolve() == args.output.resolve():
        parser.error('Input and output JSON must use different paths')
    if not args.inputs.exists() and not (args.collect_root or args.results_root):
        parser.error('Input JSON does not exist; provide --results-root to collect it')
    inputs = json.loads(args.inputs.read_text()) if args.inputs.exists() else {}
    root = (args.collect_root or ROOT).resolve()
    if args.collect_root or args.results_root:
        inputs = collect(root, inputs, args.results_root)
    results = calculate(inputs, expected_task_sets(root))
    for path, value in [(args.inputs, inputs), (args.output, results)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(value, indent=2) + '\n')
        temp.replace(path)
    print(json.dumps({m: r['summary'] for m, r in results['models'].items()}, indent=2))


if __name__ == '__main__':
    main()
