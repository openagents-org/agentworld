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
`evaluate_results*`, research reports, and visualization files. They are useful
for historical work but are not additional suites to mix into the main score.

`agents/run_*.sh` and many `scripts/run_*.sh` files are machine-specific experiment
launchers. `scripts/benchmark/` belongs to an older tooling layout. Prefer
`agents/run.py` for new experiments. `beam_verifier/` is a separate search-based
verification experiment. Root `evaluate_tasks.py` evaluates task design, not
model benchmark scores. `task_verifier.py`, `task_verifier1.py`, and
`batch_verify.sh` are legacy verification entry points; the new guide uses the
per-task verifiers through `agents/verification.py`.

Existing task/code paths stay in place to preserve historical scripts. Put new
onboarding docs under `docs/benchmark/`, examples under `examples/agents/`, and
portable evaluation entry points under `benchmarks/`. Put generated runs under
`runs/` (ignored by Git), not among source files. Install the Python runner in
`.venv/` and keep private configs in `agents/configs/*.local.yaml`.

The leaderboard and website live in
[openagents-org/agentworld-web](https://github.com/openagents-org/agentworld-web).
