"""Offline checks for checkpoint PSR, coverage, and relocated experiment traces."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.score_psr import calculate, checkpoint_score, collect, expected_task_sets


class PSRTests(unittest.TestCase):
    def test_fractional_example_and_success_override(self):
        message = 'Logs: 3/5, Kills: 0/3, All alive: True'
        result = checkpoint_score('task_01_magic_staff', message, False)
        self.assertAlmostEqual(result['PSR'], 8 / 15)
        self.assertEqual([c['credit'] for c in result['checkpoints']], [0.6, 0, 1])
        self.assertEqual(checkpoint_score('task_01_magic_staff', '', True)['PSR'], 1)

    def test_caps_booleans_round_limits_and_legacy_targets(self):
        for message, expected in [('Logs: 8/5', 1), ('All alive: False', 0),
                                  ('Rounds: 25/25', 1), ('Rounds: 26/25', 0),
                                  ('Rounds: 10/25', 1), ('Pickaxe count: 0', 0),
                                  ('Pickaxe count: 1', 1)]:
            with self.subTest(message=message):
                self.assertEqual(checkpoint_score('task_07_pickaxe_crafting', message, False)['PSR'], expected)

    def test_unknown_checkpoints_are_not_zero(self):
        for message in ['Logs: unknown', 'Logs: 1/0', 'Unknown: 3', '']:
            with self.subTest(message=message), self.assertRaises((ValueError, KeyError)):
                checkpoint_score('task_01_magic_staff', message, False)

    def row(self, task, message, success=False, stage='main', **kwargs):
        return dict(stage=stage, task=task, message=message, success=success,
                    CCE=kwargs.get('CCE', 0), rounds=10, chats=2)

    def test_tasks_weighted_equally_and_partial_coverage(self):
        tasks = sorted(expected_task_sets()['main'])
        rows = [self.row(tasks[0], 'Logs: 3/5, Kills: 0/3, All alive: True'),
                self.row(tasks[1], '', success=True)]
        summary = calculate({'example': rows})['models']['example']['summary']['main']
        self.assertAlmostEqual(summary['PSR_percent'], 100 * 23 / 30)
        self.assertEqual(summary['SR_percent'], 50)
        self.assertFalse(summary['final'])
        self.assertEqual(len(summary['missing_tasks']), 98)

    def test_complete_split_coverage(self):
        rows = [self.row(task, '', True, stage) for stage, tasks in expected_task_sets().items()
                for task in sorted(tasks)]
        summary = calculate({'example': rows})['models']['example']['summary']
        for split, expected in [('main', 100), ('augmented_v1', 100),
                                ('augmented_v2', 100), ('augmented', 200)]:
            self.assertTrue(summary[split]['final'])
            self.assertEqual(summary[split]['scored'], expected)
            self.assertEqual(summary[split]['PSR_percent'], 100)

    def test_duplicate_unknown_and_invalid_values_rejected(self):
        task = sorted(expected_task_sets()['main'])[0]
        row = self.row(task, 'Logs: 0/5')
        with self.assertRaisesRegex(ValueError, 'Duplicate task'):
            calculate({'example': [row, row]})
        with self.assertRaisesRegex(ValueError, 'Unexpected task'):
            calculate({'example': [dict(row, task='task_999_unknown')]})
        for changes in [{'success': 'false'}, {'CCE': float('nan')}, {'CCE': 1.1},
                        {'CCE': 0.5}, {'rounds': -1}, {'chats': '2'}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                calculate({'example': [dict(row, **changes)]})

    def test_relocated_collection_and_cache_invalidation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'task_verifier.py').write_text('# hash fixture')
            task = 'task_01_magic_staff_v2'
            folder = root / 'results/custom-model/augmented' / task
            attempt = folder / 'attempt_1'
            attempt.mkdir(parents=True)
            trajectory = {'task_source': task + '.yaml', 'rounds': [],
                          'metrics': {'total_rounds': 10, 'total_chats': 2}}
            trajectory_file = attempt / 'task_01_trajectory.json'
            trajectory_file.write_text(json.dumps(trajectory))
            (folder / 'completed.json').write_text(json.dumps({'task': task,
                'trajectory': '/old-host/unavailable/attempt_1/task_01_trajectory.json',
                'metrics': trajectory['metrics']}))
            (folder / 'cce.json').write_text(json.dumps({'task_source': task + '.yaml',
                                                       'success': False, 'ce': 0}))
            with patch('task_verifier.verify_task', return_value=(False, 'Logs: 0/5')) as verify:
                first = collect(root, {}, root / 'results')
                verify.assert_called_once_with(trajectory, version=2)
                verify.reset_mock()
                self.assertEqual(collect(root, first, root / 'results'), first)
                verify.assert_not_called()
                trajectory['rounds'] = [{'round': 1}]
                trajectory_file.write_text(json.dumps(trajectory))
                collect(root, first, root / 'results')
                verify.assert_called_once()
                (attempt / 'infra_error.txt').write_text('inference failed')
                with self.assertRaisesRegex(ValueError, 'Infrastructure failure'):
                    collect(root, first, root / 'results')

    def test_documented_cli_example(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'input.json'
            output = Path(tmp) / 'nested/output.json'
            source.write_text(json.dumps({'example': [self.row('task_01_magic_staff',
                'Logs: 3/5, Kills: 0/3, All alive: True')]}))
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/score_psr.py'),
                                   str(source), str(output)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(output.read_text())
            self.assertFalse(result['historical_implementation_reproduced'])
            self.assertAlmostEqual(result['models']['example']['tasks'][0]['PSR'], 8 / 15)


if __name__ == '__main__':
    unittest.main()
