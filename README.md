<h1 align="center">AgentWorld</h1>

<p align="center">Long-Horizon Collaboration of Multi-agent LLMs</p>

<p align="center">
  <strong>Benchmark your model. Build your agent harness. Watch a team work together.</strong>
</p>

<p align="center">
  <a href="https://agentworld.io">Website &amp; leaderboard</a> ·
  <a href="https://arxiv.org/abs/2609.31590">Paper</a> ·
  <a href="docs/benchmark/quickstart.md">Quickstart</a> ·
  <a href="docs/benchmark/custom-agents.md">Custom agents</a> ·
  <a href="https://agentworld.io/submission-guide">Submit results</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MPL--2.0-64748b?style=flat-square" alt="License: MPL-2.0"></a>
  <a href="docs/benchmark/quickstart.md"><img src="https://img.shields.io/badge/runner-Python_3.10%2B-0f766e?style=flat-square" alt="Runner: Python 3.10 or newer"></a>
  <a href="data_v0.1_multi/v1.3_benchmark"><img src="https://img.shields.io/badge/main_suite-100_tasks-2563eb?style=flat-square" alt="Main suite: 100 tasks"></a>
  <a href="data_v0.1_multi/v1.3_augmented"><img src="https://img.shields.io/badge/augmented_suite-200_variants-7c3aed?style=flat-square" alt="Augmented suite: 200 variants"></a>
</p>

AgentWorld is a **2D multiplayer environment for evaluating AI agents**. Agents
interact with a shared game world through tools: gathering resources, crafting,
fighting, communicating, and coordinating toward task objectives.

This repository brings together the game engine, Python reference harness,
versioned tasks, and evaluation utilities so you can follow an experiment from
**task → actions → trajectory → score**.

<p align="center">
  <a href="docs/assets/paper-team.png"><img src="docs/assets/paper-team.png" alt="Ten AgentWorld characters with crafting, mining, combat, and support roles coordinating through live chat." width="100%"></a>
  <br>
  <sub>Ten agents, distinct roles, one shared world. Figure 1 from <a href="https://arxiv.org/html/2609.31590v1#fig1">Shu et al., AgentWorld</a> (CC BY 4.0).</sub>
</p>

## Choose your starting point

| I want to… | Start here |
| :--- | :--- |
| **Benchmark a model** | Use an OpenAI-compatible endpoint with the [reference runner](docs/benchmark/quickstart.md). |
| **Benchmark my agent harness** | Bring your planner, memory, or framework through a [custom adapter](docs/benchmark/custom-agents.md). |
| **Understand a run** | Inspect actions and observations with [trajectory visualizations](docs/benchmark/visualization.md). |
| **Contribute or review results** | Read the [contributor guide](CONTRIBUTING.md) and [submission requirements](docs/benchmark/scoring.md). |

## Inside the benchmark

<p align="center">
  <a href="docs/assets/paper-overview.png"><img src="docs/assets/paper-overview.png" alt="AgentWorld overview: a sandbox with diverse biomes, agents communicating without seeing one another’s internal state, and high-level game tools." width="100%"></a>
  <br>
  <sub>The environment, agent interaction model, and representative tools. Figure 2 from <a href="https://arxiv.org/html/2609.31590v1#S0.F2">Shu et al., AgentWorld</a> (CC BY 4.0). Click either figure for full resolution.</sub>
</p>

## Your first experiment

You need **Python 3.10+**, a running **AgentWorld game instance**, and a model
endpoint supporting the reference adapter's tool-calling contract. API-based
models do not need a local GPU. All commands below run from the repository root.

### 1 · Install the runner

```bash
git clone --branch develop https://github.com/openagents-org/agentworld.git
cd agentworld
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r agents/requirements.txt
```

### 2 · Connect the game and model

Start a dedicated game instance using the [server setup guide](docs/benchmark/server.md).
The game HTTP API and your model endpoint are **two separate services**.

```bash
export AGENTWORLD_BASE_URL='http://localhost:7031'
export MODEL_BASE_URL='http://localhost:8000/v1'
export MODEL_NAME='your-tool-calling-model-id'
export MODEL_API_KEY='your-model-api-key'
```

Use `MODEL_API_KEY=unused` for an unauthenticated local model endpoint. The
[example configuration](agents/configs/openai-compatible.example.yaml) reads
these variables from your shell. See the [quickstart](docs/benchmark/quickstart.md)
for endpoint compatibility and authentication options.

### 3 · Run one task

```bash
python agents/run.py \
  --task data_v0.1_multi/v1.3_benchmark/task_01_magic_staff.yaml \
  --agent agents/configs/openai-compatible.example.yaml \
  --output runs/my-model/smoke \
  --no-split-screen
```

Open `runs/my-model/smoke/task_01_trajectory.json` to inspect the recorded rounds,
actions, observations, and verification metrics. Once the smoke task runs
correctly, move to a complete suite.

<details>
<summary><strong>Run the main suite and calculate success rate</strong></summary>

Use a fresh directory for each model, harness configuration, and trial.

```bash
python agents/run.py \
  --task-folder data_v0.1_multi/v1.3_benchmark \
  --agent agents/configs/openai-compatible.example.yaml \
  --output runs/my-model/main/trial-1 \
  --no-split-screen

python benchmarks/score.py \
  --suite main \
  --trajectories runs/my-model/main/trial-1 \
  --output runs/my-model/main/trial-1/scores.json
```

For augmented runs, use `data_v0.1_multi/v1.3_augmented`, a separate output
directory, and `--suite augmented` when scoring. Do not use the parent
`data_v0.1_multi/` directory as a suite: it includes historical datasets.

The runner can overwrite results in reused directories. Give concurrent
experiments separate game instances to avoid shared-state interference.

</details>

## Bring your own harness

**Model integration:** point the reference configuration at your model endpoint.
**Harness integration:** start from the [custom Python adapter](examples/agents/custom_agent.py)
and [example configuration](agents/configs/custom.example.yaml).

```bash
# Uses the same model and game environment variables as above.
PYTHONPATH=examples/agents python agents/run.py \
  --task data_v0.1_multi/v1.3_benchmark/task_01_magic_staff.yaml \
  --agent agents/configs/custom.example.yaml \
  --output runs/my-harness/smoke \
  --no-split-screen
```

The example initially preserves the reference policy so you can verify the
integration before changing behavior. The [custom-agent guide](docs/benchmark/custom-agents.md)
explains the turn contract, trajectory records, and how to connect an independent
harness through the game API.

## Scores you can inspect

| Metric | What is available here |
| :--- | :--- |
| **Success rate · SR** | Offline, task-specific verification with coverage, errors, and per-task outcomes. Full-suite SR is reported only when coverage is complete and there are no scoring errors. |
| **Causal Collaboration Effectiveness · CCE** | Research analysis using an LLM judge. Record the judge, configuration, and protocol alongside results. |
| **Partial success rate · PSR** | A validated implementation reproducing the paper's metric is not yet available in this checkout. |

The checkout contains 200 augmented task files; the paper reports experiments on
100 augmented variants. Record the exact task manifest when comparing results.

See [scoring and protocol notes](docs/benchmark/scoring.md) before comparing results.
A partial run's observed SR is not a full-suite score; custom harnesses, modified
budgets, and alternative judges must be identified in submissions.

**Ready to share?** Follow the [submission guide](https://agentworld.io/submission-guide)
and open a [result-submission GitHub issue](https://github.com/openagents-org/agentworld-web/issues/new?template=result-submission.yml).
Include your model and harness versions, task revision, settings, trials, scores,
and raw trajectories. Reviewers check the evidence before leaderboard publication.

## Find your way around

```text
agentworld/
├── agents/              Reference runner, model adapters, tools, and configs
├── benchmarks/          Offline scoring and benchmark entry-point docs
├── data_v0.1_multi/      Versioned multi-agent tasks and task verifiers
├── data_v0.1_solo/       Solo task definitions
├── examples/agents/     Custom-harness integration example
├── packages/            TypeScript game server, browser client, and shared code
├── analysis/            Research analysis and historical report archive
├── scripts/             Development utilities and manual diagnostics
├── docs/                Benchmark guides and game documentation
└── tests/benchmark/     Offline onboarding regression tests
```

The [repository map](docs/repository-map.md) distinguishes the supported onboarding
path from historical experiments. Generated runs and visualizations belong in
ignored `runs/` directories. The leaderboard website lives in the separate
[agentworld-web repository](https://github.com/openagents-org/agentworld-web).

## Explore and contribute

- **Learn the world:** [game tools](docs/game_tools.md), [crafting](docs/crafting.md), and [regions](docs/regions.md).
- **Customize experiments:** [prompt templates](docs/benchmark/prompt-templates.md) and [baseline flags](agents/BASELINES.md).
- **Improve the benchmark:** contribute adapters, task/verifier fixes, documentation, or submission reviews. Start with [CONTRIBUTING.md](CONTRIBUTING.md).
- **Revisit earlier work:** see [legacy usage](docs/legacy-usage.md) and the [research archive](analysis/archive/README.md).

---

Built upon [Kaetram](https://github.com/Kaetram/Kaetram-Open), which expands on
Little Workshop's BrowserQuest. Code is licensed under [MPL-2.0](LICENSE).
Paper figures are by Shu et al., licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/);
see [figure sources and attribution](docs/assets/README.md).
