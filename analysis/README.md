# Research analysis

- `scripts/`: CCE analysis and task-quality review tooling.
- `results/`: Existing research analysis results.
- `archive/`: Historical task reviews, investigations, and category notes moved
  out of the repository root.

For current model scoring, start with [Scoring and results](../docs/benchmark/scoring.md).
`analysis/scripts/evaluate_tasks.py` reviews task design using the Claude CLI;
it does **not** run an agent benchmark or calculate model scores.

```bash
python analysis/scripts/evaluate_tasks.py --help
```

Its default repository is inferred from the script path. New reports go under
ignored `runs/task-reviews/benchmark/` or `runs/task-reviews/augmented/`.
`--base-dir` and `--results-dir` override those locations. Running an evaluation
requires a configured Claude CLI and may incur model usage.
