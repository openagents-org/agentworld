"""CCE entry-point checks use no judge or game calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'analysis/scripts/compute_cce_v2.py'


@unittest.skipUnless(importlib.util.find_spec('openai'), 'Install analysis/requirements-cce.txt')
class CCEEntryTests(unittest.TestCase):
    def test_import_requires_no_credentials_or_client(self):
        with patch.dict(os.environ, {}, clear=True):
            spec = importlib.util.spec_from_file_location('test_cce', SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertIsNone(module.client)
            with self.assertRaisesRegex(ValueError, 'CCE_API_KEY'):
                module.call_llm('unused')

    def test_explicit_trajectory_scores_failure_without_model_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'task_01_trajectory.json'
            output = Path(tmp) / 'cce.json'
            path.write_text(json.dumps({'task_id': 'task_01', 'task_definition': {},
                'metrics': {'task_verified_success': False}, 'rounds': []}))
            env = {k: v for k, v in os.environ.items() if not k.startswith('CCE_')}
            result = subprocess.run([sys.executable, str(SCRIPT), '--trajectory', str(path),
                '--output', str(output)], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text())
            self.assertIsNone(report['model'])
            self.assertEqual(report['trajectory'], str(path))
            self.assertEqual(report['results'][0]['ce'], 0)
