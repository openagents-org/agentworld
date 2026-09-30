#!/usr/bin/env python3
"""Offline SR from repository task verifiers; does not calculate PSR or CCE."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'agents'))
from verification import verify_trajectory

SUITES = {
    'main': ROOT / 'data_v0.1_multi/v1.3_benchmark',
    'augmented': ROOT / 'data_v0.1_multi/v1.3_augmented',
}


def task_key(trajectory, catalog):
    key = trajectory.get('task_key')
    if not key and trajectory.get('task_source'):
        key = Path(trajectory['task_source']).stem
    if key:
        if key not in catalog:
            raise ValueError(f'Task {key} is not in the selected suite')
        return key
    # Old main logs have only task_NN. Never guess between augmented variants.
    identifier = trajectory.get('task_id', '')
    if not re.fullmatch(r'task_\d+', identifier):
        raise ValueError('Missing task_key/task_source and invalid task_id')
    matches = [k for k in catalog if k.startswith(identifier + '_')]
    if len(matches) != 1:
        raise ValueError(f'Ambiguous or unknown task_id {identifier}; supply task_key')
    return matches[0]


def score(directory, suite):
    catalog = {p.stem: p for p in SUITES[suite].glob('*.yaml')}
    if not catalog:
        raise ValueError('Selected suite has no tasks')
    rows, errors, seen = [], [], set()
    for path in sorted(Path(directory).rglob('*_trajectory.json')):
        try:
            trajectory = json.loads(path.read_text())
            key = task_key(trajectory, catalog)
            if key in seen:
                raise ValueError(f'Duplicate trajectory for {key}; score one trial at a time')
            seen.add(key)
            if not isinstance(trajectory.get('rounds'), list) or not trajectory['rounds']:
                raise ValueError('No recorded rounds; incomplete or invalid trajectory')
            passed, details = verify_trajectory(trajectory, catalog[key])
            rows.append({'task': key, 'success': passed, 'details': details, 'file': str(path)})
        except Exception as error:
            errors.append({'file': str(path), 'error': str(error)})
    missing = sorted(set(catalog) - {r['task'] for r in rows})
    complete = not missing and not errors
    successes = sum(row['success'] for row in rows)
    return {
        'suite': suite, 'metric': 'repository_verifier_SR',
        'expected_tasks': len(catalog), 'scored_tasks': len(rows),
        'successes': successes, 'complete': complete,
        'SR_percent': 100 * successes / len(catalog) if complete else None,
        'observed_SR_percent': 100 * successes / len(rows) if rows and not errors else None,
        'missing_tasks': missing, 'errors': errors, 'results': rows,
        'note': 'Uses this checkout\'s task verifiers. Not a certification of paper-protocol equivalence.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=SUITES, required=True)
    parser.add_argument('--trajectories', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.trajectories.is_dir():
        parser.error('--trajectories must be an existing directory')
    report = score(args.trajectories, args.suite)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('suite', 'scored_tasks', 'expected_tasks', 'complete', 'SR_percent', 'observed_SR_percent')}, indent=2))
    if report['errors'] or not report['scored_tasks']:
        print(f"Scoring needs attention; see {args.output}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
