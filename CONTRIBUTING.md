# Contributing to AgentWorld

Start with the [repository map](docs/repository-map.md) and
[benchmark quickstart](docs/benchmark/quickstart.md).

- **Model or harness integrations:** supply a minimal adapter/configuration,
  a smoke-task trajectory, and the exact reproduction command.
- **Task/verifier fixes:** include a failing example and a regression check.
  Describe which scores or historical runs may be affected; do not silently
  change benchmark criteria as part of a formatting cleanup.
- **Documentation:** use root-relative commands and environment-based examples.
  Separate portable workflows from machine-specific experiment launchers.
- **Result reviews:** use the [GitHub issue submission workflow](docs/benchmark/scoring.md).
  Check configuration, coverage, protocol, and raw evidence before publication.

Run the offline onboarding checks without game credentials or model calls:

```bash
python -m pip install -r agents/requirements.txt
python -m unittest discover -s tests/benchmark -v
python agents/run.py --help
python benchmarks/score.py --help
```

Live game/model runs are separate validation. Include the task/harness revision,
settings, and coverage with those results. Keep credentials, virtual environments,
and generated run artifacts out of commits.
