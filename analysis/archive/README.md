# Historical analysis archive

These are retained research notes and task-quality evaluations, not current
leaderboard results. Existing report contents are preserved, including descriptions
of older runs and their original filesystem paths.

| Location | Previous root location | Contents |
| --- | --- | --- |
| `task-reviews/main/` | `evaluate_results/` | Main-task evaluation reports and summaries |
| `task-reviews/augmented/` | `evaluate_results_augmented/` | Augmented-task evaluation reports and summaries |
| `investigations/` | `investigate_results/` | Task 57–59 investigation notes |
| `task_categories.txt` | `task_categories.txt` | Historical 106-task categorization; not the current suite manifest |

New task-quality evaluations should write to `runs/task-reviews/` using
`analysis/scripts/evaluate_tasks.py`. Current model scoring instructions are in
[Scoring and results](../../docs/benchmark/scoring.md).

Generated root HTML visualizations and `agents/error_captures/` response dumps
were removed from the tracked tree. Their old versions remain in Git history.
To recover a specific visualization without putting it back in the root:

```bash
mkdir -p runs/visualizations
git show e1935203:viz_task_05.html > runs/visualizations/viz_task_05.html
```

For new reports, use the [trajectory visualization guide](../../docs/benchmark/visualization.md).
