# Benchmark entry points

1. [Run a model](../docs/benchmark/quickstart.md) with `agents/run.py`.
2. [Integrate a harness](../docs/benchmark/custom-agents.md) through `BaseAgent`.
3. [Score and submit](../docs/benchmark/scoring.md) with `benchmarks/score.py`.

Task definitions remain in their existing versioned directories. This directory
provides a discoverable entry point without moving datasets or changing task
criteria. `score.py` performs offline success-rate reporting only; it makes no
model API calls.
