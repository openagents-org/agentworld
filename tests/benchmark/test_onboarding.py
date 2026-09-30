"""Offline checks for the portable benchmark entry points. No service calls."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents'))
sys.path.insert(0, str(ROOT / 'examples/agents'))
sys.path.insert(0, str(ROOT / 'benchmarks'))
from agent_factory import AgentFactory
from config_loader import load_agent_config
from run import TaskRunner
from verification import verifier_for_task, verify_trajectory
import score

MAIN = ROOT / 'data_v0.1_multi/v1.3_benchmark'
AUG = ROOT / 'data_v0.1_multi/v1.3_augmented'


def trajectory(key='task_01_magic_staff', passed=True):
    return {'task_id': 'task_01', 'task_key': key, 'rounds': [{'actions': [{
        'agent_name': 'wizard', 'observation': {'inventory': {'items': [
            {'key': 'staff', 'count': 1}] if passed else []}}}]}], 'metrics': {}}


class ConfigTests(unittest.TestCase):
    def test_example_env_substitution_keeps_yaml_structure(self):
        values = {'MODEL_NAME': 'test-model', 'MODEL_API_KEY': 'key: #\\n${UNSET}',
                  'MODEL_BASE_URL': 'http://localhost:8000/v1',
                  'AGENTWORLD_BASE_URL': 'http://localhost:7031'}
        with patch.dict(os.environ, values):
            data = load_agent_config(ROOT / 'agents/configs/openai-compatible.example.yaml')['agent']
        self.assertEqual(data['llm']['api_key'], values['MODEL_API_KEY'])
        self.assertEqual(data['game']['host'], values['AGENTWORLD_BASE_URL'])

    def test_missing_variable_fails_before_execution(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'MODEL_NAME'):
                load_agent_config(ROOT / 'agents/configs/openai-compatible.example.yaml')

    def test_literal_legacy_config_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.yaml'
            path.write_text('agent:\n  name: example\n  llm:\n    model: literal\n')
            self.assertEqual(load_agent_config(path)['agent']['llm']['model'], 'literal')


class AdapterTests(unittest.TestCase):
    def test_explicit_model_and_game_endpoints_are_separate(self):
        with patch('requests.Session.request', side_effect=AssertionError('Network used')):
            agent = AgentFactory.create_agent('openai', api_key='test', model='test',
                base_url='http://game:7031', llm_params={'base_url': 'http://model:8000/v1/'})
        self.assertEqual(agent.base_url, 'http://model:8000/v1')
        self.assertEqual(agent.game_tools.base_url, 'http://game:7031')
        self.assertEqual(agent.session.headers['Authorization'], 'Bearer test')
        self.assertNotIn('X-API-Key', agent.session.headers)

    def test_legacy_gateway_auth_preserved(self):
        agent = AgentFactory.create_agent('openai', api_key='test')
        self.assertEqual(agent.session.headers['X-API-Key'], 'test')
        self.assertNotIn('Authorization', agent.session.headers)

    def test_custom_adapter_receives_config(self):
        agent = AgentFactory.create_agent('custom', api_key='test', model='custom-model',
            llm_params={'agent_class': 'custom_agent:CustomAgent',
                        'base_url': 'http://model/v1', 'auth_header': 'X-API-Key'})
        self.assertEqual(type(agent).__name__, 'CustomAgent')
        self.assertEqual(agent.model, 'custom-model')
        self.assertEqual(agent.base_url, 'http://model/v1')
        self.assertEqual(agent.session.headers['X-API-Key'], 'test')

    def test_invalid_custom_class_rejected(self):
        for target in ['wrong', 'pathlib:Path']:
            with self.subTest(target=target), self.assertRaises(ValueError):
                AgentFactory.create_agent('custom', llm_params={'agent_class': target})


class VerifierTests(unittest.TestCase):
    def test_all_catalog_tasks_have_verifiers(self):
        for directory, count in [(MAIN, 100), (AUG, 200)]:
            tasks = list(directory.glob('*.yaml'))
            self.assertEqual(len(tasks), count)
            for task in tasks:
                self.assertTrue(verifier_for_task(task).is_file(), task.name)

    def test_actual_main_verifier_positive_and_negative(self):
        task = MAIN / 'task_01_magic_staff.yaml'
        self.assertTrue(verify_trajectory(trajectory(), task)[0])
        self.assertFalse(verify_trajectory(trajectory(passed=False), task)[0])

    def test_augmented_uses_adjacent_verifier(self):
        for suffix in ['v1', 'v2']:
            task = AUG / f'task_01_magic_staff_{suffix}.yaml'
            self.assertEqual(verifier_for_task(task), task.with_name(task.stem + '_success_criteria.py'))

    def test_unknown_variant_never_falls_back_to_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                verifier_for_task(Path(tmp) / 'task_01_unknown_v2.yaml')

    def test_runner_preserves_variants_and_metadata(self):
        runner = TaskRunner.__new__(TaskRunner)
        runner.logger = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            runner.output_dir = Path(tmp)
            for suffix in ['v1', 'v2']:
                key = f'task_01_magic_staff_{suffix}'
                runner._init_trajectory(str(AUG / (key + '.yaml')), None)
                self.assertEqual(runner.trajectory_data['task_key'], key)
                self.assertEqual(runner.trajectory_data['task_source'], str(AUG / (key + '.yaml')))
                runner.trajectory_data['rounds'] = trajectory()['rounds']
                self.assertTrue(runner._check_task_success_early()[0])
                runner._save_trajectory(None, {})
            self.assertEqual(len(list(Path(tmp).glob('*_trajectory.json'))), 2)
            runner._init_trajectory(str(MAIN / 'task_01_magic_staff.yaml'), None)
            runner._save_trajectory(None, {})
            self.assertTrue((Path(tmp) / 'task_01_trajectory.json').exists())


class ScoreTests(unittest.TestCase):
    def write(self, directory, name, data):
        path = directory / (name + '_trajectory.json')
        path.write_text(json.dumps(data))
        return path

    def test_partial_coverage_not_published_as_full_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(Path(tmp), 'one', trajectory())
            report = score.score(tmp, 'main')
        self.assertFalse(report['complete'])
        self.assertIsNone(report['SR_percent'])
        self.assertEqual(report['observed_SR_percent'], 100)
        self.assertEqual(len(report['missing_tasks']), 99)

    def test_complete_suite_uses_expected_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i, task in enumerate(sorted(MAIN.glob('*.yaml'))):
                self.write(Path(tmp), task.stem, trajectory(task.stem, passed=i < 50))
            with patch.object(score, 'verify_trajectory', side_effect=lambda t, p: (
                    bool(t['rounds'][0]['actions'][0]['observation']['inventory']['items']), 'fixture')):
                report = score.score(tmp, 'main')
        self.assertTrue(report['complete'])
        self.assertEqual(report['SR_percent'], 50)

    def test_duplicate_attempts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(Path(tmp), 'one', trajectory())
            self.write(Path(tmp), 'two', trajectory())
            report = score.score(tmp, 'main')
        self.assertIn('Duplicate', report['errors'][0]['error'])
        self.assertIsNone(report['observed_SR_percent'])

    def test_ambiguous_augmented_legacy_id_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = trajectory(); del data['task_key']
            self.write(Path(tmp), 'one', data)
            report = score.score(tmp, 'augmented')
        self.assertIn('Ambiguous', report['errors'][0]['error'])

    def test_malformed_and_empty_trajectories_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'bad_trajectory.json').write_text('{')
            data = trajectory(); data['rounds'] = []
            self.write(Path(tmp), 'empty', data)
            report = score.score(tmp, 'main')
        self.assertEqual(len(report['errors']), 2)
        self.assertEqual(report['scored_tasks'], 0)

    def test_saved_absolute_source_does_not_execute_external_verifier(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = trajectory(); del data['task_key']
            data['task_source'] = '/another-machine/task_01_magic_staff.yaml'
            self.write(Path(tmp), 'one', data)
            report = score.score(tmp, 'main')
        self.assertEqual(report['successes'], 1)
        self.assertEqual(report['errors'], [])

    def test_wrong_suite_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(Path(tmp), 'one', trajectory('task_01_magic_staff_v1'))
            report = score.score(tmp, 'main')
        self.assertIn('not in the selected suite', report['errors'][0]['error'])


if __name__ == '__main__':
    unittest.main()
