# Integrating a model or agent harness

## A model behind an OpenAI-compatible endpoint

Use `agents/configs/openai-compatible.example.yaml` and the
[quickstart](quickstart.md). You do not need to modify the factory or game engine.
Keep the endpoint's model ID separate from the name you use on the leaderboard.

## A custom Python adapter in the reference runner

Set `agent.provider: custom` and `agent.llm.agent_class: module:Class`. The
factory imports that class from your Python path. Configs selecting custom classes
execute local Python code; use an adapter you trust.

A runnable starting point is `examples/agents/custom_agent.py`. It inherits the
OpenAI-compatible policy unchanged so you can first verify wiring:

```bash
# Set the same model/game variables as in the quickstart.
PYTHONPATH=examples/agents python agents/run.py \
  --task data_v0.1_multi/v1.3_benchmark/task_01_magic_staff.yaml \
  --agent agents/configs/custom.example.yaml \
  --output runs/my-harness/smoke \
  --no-split-screen
```

Your class must inherit `BaseAgent` and accept these constructor keywords:
`api_key`, `model`, `username`, `password`, `base_url`, `dump_prompts`, and
`llm_params`. `base_url` is the **game** URL; model settings live in `llm_params`.
A custom harness may omit `api_key` from its YAML if it does not require one.
The runner still requires `llm.model` as its configured model identifier.

The integration points are:

- `_make_api_call(messages)`: return an OpenAI-shaped response with
  `choices[0].message` and its tool calls. See `agents/openai_agent.py`.
- `_extract_tool_calls(message)`: normalize calls to dictionaries with `id`,
  `name`, and parsed `arguments`. See the existing provider adapters.
- `execute_single_tool_call(user_input)`: the runner calls this once per agent
  turn. The inherited implementation executes one action, records conversation
  history, and emits the action/result information used in trajectories.

For a different planner, memory system, or agent framework, wrap it behind that
contract. Keep `game_tools`, tool definitions, experiment restriction flags,
and action recording intact. Overriding only `process_user_input()` does not
change the benchmark's round-based execution path. If you replace
`execute_single_tool_call`, preserve its one-action-per-turn behavior and the
`[TOOL_CALL_INFO]` / `[TOOL_RESULT]` records consumed by `agents/run.py`.

Changing prompts or policy is a harness change: report it together with model
settings, action/round budget, source commit, and repetitions. Extra model calls
or hidden game actions must be disclosed; do not treat them as the reference
harness protocol.

## An independent harness

Use `agents/game_tools.py`, `agents/tool_definitions.py`, and the
[server API reference](../../packages/server/src/network/README-AI-API.md) as the
integration surface. The task YAML defines objectives, initial characters,
inventories, skill levels, and starting positions.

Independent harnesses must reproduce that initialization and record the same
observations/actions needed by the task verifiers. The offline SR scorer expects
`*_trajectory.json` files containing `task_key` (the task YAML stem) and non-empty
`rounds`, with each round's `actions` including `agent_name` and `observation`.
This is a minimum identification shape, not the entire verifier contract: retain
all fields emitted by the reference runner and inspect the relevant task verifier.
Do not use a result-only JSON file as a substitute for the trajectory.

For YAML prompt customization, see [Prompt templates](prompt-templates.md).
