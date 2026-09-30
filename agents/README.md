# Python agents and benchmark runner

Start with the [benchmark quickstart](../docs/benchmark/quickstart.md).

| File | Responsibility |
| --- | --- |
| `run.py` | Task initialization, round scheduling, trajectories, early stopping |
| `config_loader.py` | YAML and explicit environment-variable references |
| `agent_factory.py` | Built-in providers and custom adapter loading |
| `base_agent.py` | Shared prompts, tool execution, and one-action-per-turn contract |
| `*_agent.py` | Provider-specific model requests and response conversion |
| `game_tools.py`, `tool_definitions.py` | Game API client and agent-visible actions |
| `experiment.py` | Baselines, round budgets, communication and spawn controls |
| `verification.py` | Task-specific verifier selection shared with offline scoring |
| `console.py` | Interactive debugging and character initialization |

Use `configs/openai-compatible.example.yaml` for an HTTP model endpoint, or
`configs/custom.example.yaml` with the [custom-agent guide](../docs/benchmark/custom-agents.md).
Install `requirements.txt` for API models; `requirements-local.txt` additionally
installs vLLM for the `deepseek_local` provider.

The `run_*.sh` and rerun scripts are historical experiment launchers, often with
absolute paths and machine-specific settings. Use `python agents/run.py --help`
from the repository root as the portable entry point.

See [BASELINES.md](BASELINES.md) for experiment variants. Record all non-default
flags when reporting results.

The earlier provider-specific documentation is retained in the
[historical Qwen guide](../docs/legacy-qwen-agent.md).
