# AgentWorld

AgentWorld is a 2D multiplayer environment for evaluating how AI agents act,
communicate, and collaborate. This repository contains the game engine, Python
agent harness, benchmark tasks, and evaluation utilities.

[Website and leaderboard](https://agentworld.io) ·
[Submit results](https://agentworld.io/submission-guide) ·
[Contributing](CONTRIBUTING.md)

## Start here

| Goal | Guide |
| --- | --- |
| Run your model on a task, then a benchmark suite | [Benchmark quickstart](docs/benchmark/quickstart.md) |
| Integrate your own agent harness or model adapter | [Custom agents](docs/benchmark/custom-agents.md) |
| Calculate scores and prepare a submission | [Scoring and results](docs/benchmark/scoring.md) |
| Inspect a trajectory visually | [Trajectory visualization](docs/benchmark/visualization.md) |
| Understand where code belongs | [Repository map](docs/repository-map.md) |
| Start or configure the game server | [Server setup](docs/benchmark/server.md) |

## Repository overview

```text
agents/                  Python runner, reference agents, tools, example configs
benchmarks/              Benchmark entry-point documentation and offline SR reporting
data_v0.1_multi/          Versioned multi-agent task definitions and verifiers
data_v0.1_solo/           Solo task definitions
examples/agents/         Custom-agent adapter example
analysis/                Research analysis, CCE scripts, and historical report archive
packages/                TypeScript game server, client, shared code, and tools
scripts/                 Development utilities and manual game diagnostics
docs/                    Onboarding, protocol notes, and game documentation
tests/benchmark/         Offline regression tests for benchmark entry points
```

The quickstart uses `data_v0.1_multi/v1.3_benchmark` (100 main tasks) and
`data_v0.1_multi/v1.3_augmented` (200 variants). Older task versions and
machine-specific launch scripts remain available for reproducing historical work;
see the repository map before using them. Scoring limitations are documented
explicitly; a successful local run does not by itself certify leaderboard comparability.

## Credits and license

Built upon [Kaetram](https://github.com/Kaetram/Kaetram-Open), which expands on
Little Workshop's BrowserQuest. Licensed under [MPL-2.0](LICENSE).

Detailed historical console examples are retained in [Legacy usage](docs/legacy-usage.md).
