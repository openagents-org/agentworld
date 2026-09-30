# Repository map

## Supported onboarding path

| Area | Start here | Role |
| --- | --- | --- |
| Benchmark execution | `agents/run.py` | Load tasks/configuration, initialize characters, schedule turns, record trajectories |
| Model/harness adapters | `agents/agent_factory.py`, `agents/base_agent.py` | Provider integration and shared agent contract |
| Game actions | `agents/game_tools.py`, `agents/tool_definitions.py` | HTTP client and tool schemas |
| Main task set | `data_v0.1_multi/v1.3_benchmark/` | 100 YAMLs, per-task verifiers, shared verifier utilities |
| Augmented task set | `data_v0.1_multi/v1.3_augmented/` | 200 YAML variants with adjacent verifiers |
| Offline SR reporting | `benchmarks/score.py` | Coverage, errors, per-task outcomes, complete-suite SR |
| CCE research code | `analysis/scripts/compute_cce_v2.py` | LLM judge calculation |
| Game engine | `packages/server/`, `packages/common/` | Game state, networking, shared definitions |
| Browser client | `packages/client/` | Play/debug UI; the leaderboard website is a separate repository |
| Additional engine components | `packages/hub/`, `packages/tools/`, `packages/e2e/` | Hub, asset tools, engine tests |
| Contributor examples/tests | `examples/agents/`, `tests/benchmark/` | Adapter example and offline onboarding regression tests |

## Historical and specialized material

The repository retains older datasets (`v1_benchmark`, `v1.2_benchmark`, rewritten
and augmented-generation directories), solo tasks, task-generation utilities,
`analysis/archive/`, and research reports. They are useful
for historical work but are not additional suites to mix into the main score.

`agents/run_*.sh` and many `scripts/run_*.sh` files are machine-specific experiment
launchers. `scripts/benchmark/` belongs to an older tooling layout. Prefer
`agents/run.py` for new experiments. `beam_verifier/` is a separate search-based
verification experiment. `analysis/scripts/evaluate_tasks.py` evaluates task design,
not model benchmark scores. Manual attack, harvest, and tile diagnostics live in
`scripts/diagnostics/`. The historical batch wrapper is now
`scripts/legacy/batch_verify.sh`.

Root `task_verifier.py` and `task_verifier1.py` remain because existing visualizer,
analysis, and beam-verifier code imports them. The maintained benchmark guide
uses per-task verifiers through `agents/verification.py`. Generated HTML snapshots
and captured API-error responses are not tracked; see the
[visualization guide](benchmark/visualization.md) to generate a fresh report and
[archive notes](../analysis/archive/README.md) for historical file locations.

Benchmark task definitions, runner paths, and imported verifier modules stay in
place. The archive and script READMEs document relocated utilities. Put new
onboarding docs under `docs/benchmark/`, examples under `examples/agents/`, and
portable evaluation entry points under `benchmarks/`. Put generated runs under
`runs/` (ignored by Git), not among source files. Install the Python runner in
`.venv/` and keep private configs in `agents/configs/*.local.yaml`.

The leaderboard and website live in
[openagents-org/agentworld-web](https://github.com/openagents-org/agentworld-web).

Prompt configuration details are in [Prompt templates](benchmark/prompt-templates.md).
