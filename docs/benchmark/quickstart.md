# Benchmark quickstart

Run commands from the repository root. Start with one task before spending on a
full suite. This guide uses the reference harness; custom harness integration is
covered in [Custom agents](custom-agents.md).

## 1. Install the Python runner

Use Python 3.10 or newer (the offline onboarding checks use Python 3.14).

```bash
git clone --branch develop https://github.com/openagents-org/agentworld.git
cd agentworld
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r agents/requirements.txt
python agents/run.py --help
```

API-based models do not require CUDA, PyTorch, or vLLM. To use the existing
in-process `deepseek_local` provider, install `agents/requirements-local.txt`
instead. An externally hosted OpenAI-compatible model server can use the normal
CPU-only runner installation.

## 2. Start a game instance

Follow [Server setup](server.md). The default game HTTP API is
`http://localhost:7031`; this is separate from the model inference endpoint.
Use an isolated game instance for each concurrent experiment: shared world state
and reused task character names can interfere with another run.

## 3. Configure your model

The example resolves `${NAME}` values from the current shell after parsing YAML.
Missing or empty variables fail before agent initialization. `.env` is used by
the game server; the Python runner does not automatically load it.

```bash
export MODEL_NAME='your-tool-calling-model-id'
export MODEL_BASE_URL='http://localhost:8000/v1'
export MODEL_API_KEY='your-model-api-key'
export AGENTWORLD_BASE_URL='http://localhost:7031'
```

For a local endpoint without authentication, set `MODEL_API_KEY=unused`.
For OpenAI's API, set `MODEL_BASE_URL=https://api.openai.com/v1` and use your key
and a supported model ID. The adapter sends Chat Completions requests with
function tools, required tool choice, and `parallel_tool_calls=false`; your
endpoint must support that contract. It is not a Responses API adapter.

The example's `llm.base_url` and `llm.auth_header` configure the model endpoint;
`game.host` configures AgentWorld. `Authorization` sends a Bearer token;
`X-API-Key` supports gateways that require that header.

## 4. Run a smoke task

```bash
python agents/run.py \
  --task data_v0.1_multi/v1.3_benchmark/task_01_magic_staff.yaml \
  --agent agents/configs/openai-compatible.example.yaml \
  --output runs/my-model/smoke \
  --no-split-screen
```

Inspect `runs/my-model/smoke/task_01_trajectory.json`: it should contain recorded
rounds, observations, actions, task metadata, and verification metrics. Task
initialization/model errors are not successful benchmark attempts.

## 5. Run one complete trial

Use a fresh output directory for every model, harness configuration, and trial.
The runner does not resume or protect a reused output directory from overwrites.

```bash
python agents/run.py \
  --task-folder data_v0.1_multi/v1.3_benchmark \
  --agent agents/configs/openai-compatible.example.yaml \
  --output runs/my-model/main/trial-1 \
  --no-split-screen
```

The main directory contains 100 task YAMLs. For the 200 augmented variants, use
`data_v0.1_multi/v1.3_augmented` and a separate output directory, for example
`runs/my-model/augmented/trial-1`. Variant trajectories retain the full task name
including `_v1` or `_v2` so they do not overwrite each other.

Do not use the parent `data_v0.1_multi/` directory as a suite. It contains several
historical datasets. Do not change tasks, starting state, prompts, tools, or round
budgets without reporting the resulting protocol change. See
[baselines](../../agents/BASELINES.md) for supported experiment flags.

## 6. Score and submit

```bash
python benchmarks/score.py \
  --suite main \
  --trajectories runs/my-model/main/trial-1 \
  --output runs/my-model/main/trial-1/scores.json
```

The report distinguishes coverage from success rate. See
[Scoring and results](scoring.md) for incomplete runs, CCE, PSR, repeated trials,
and the GitHub issue submission route.
