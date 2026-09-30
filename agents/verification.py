"""Shared verifier selection for runner early stopping and offline SR scoring."""
import importlib.util
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'data_v0.1_multi/v1.3_benchmark'


def verifier_for_task(task_path):
    task_path = Path(task_path)
    adjacent = task_path.with_name(task_path.stem + '_success_criteria.py')
    if adjacent.is_file():
        return adjacent
    # Main tasks use task_NN_success_criteria.py rather than the full task name.
    match = re.fullmatch(r'task_(\d+)_.+', task_path.stem)
    if task_path.parent.resolve() == MAIN and match:
        verifier = MAIN / f'task_{int(match[1]):02d}_success_criteria.py'
        if verifier.is_file():
            return verifier
    raise ValueError(f'No task-specific verifier for {task_path.name}')


@lru_cache(maxsize=None)
def _load_verifier(path):
    if 'verifier_utils' not in sys.modules:
        spec = importlib.util.spec_from_file_location('verifier_utils', MAIN / 'verifier_utils.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules['verifier_utils'] = module
        spec.loader.exec_module(module)
    spec = importlib.util.spec_from_file_location('agentworld_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def verify_trajectory(trajectory, task_path=None):
    # Explicit catalog paths take precedence over paths saved on other machines.
    source = task_path or trajectory.get('task_source')
    if source:
        verifier = verifier_for_task(source)
    else:
        # Compatibility with historical main-task logs lacking source metadata.
        match = re.fullmatch(r'task_(\d+)', trajectory.get('task_id', ''))
        if not match:
            raise ValueError('A task source is required to select the verifier')
        verifier = MAIN / f'task_{int(match[1]):02d}_success_criteria.py'
        if not verifier.is_file():
            raise ValueError('Unknown task ID')
    passed, details = _load_verifier(verifier)(trajectory)
    return bool(passed), details
