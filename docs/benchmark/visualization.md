# Visualizing a trajectory

Generated HTML reports belong under `runs/`, next to experiment output, rather
than in the repository root. The source visualizer remains
`agents/visualize_trajectory.py`.

After running the quickstart smoke task:

```bash
mkdir -p runs/visualizations
python agents/visualize_trajectory.py \
  runs/my-model/smoke/task_01_trajectory.json \
  --output runs/visualizations/task_01.html \
  --sprites-path ../../packages/client/public/img/sprites/items
```

Open the generated HTML in a browser. The example sprite path is relative to
`runs/visualizations/`; adjust it if the HTML is moved or served elsewhere.
Omitting `--output` writes HTML beside the input trajectory. The output directory
must already exist.

The visualizer includes a historical verifier result for debugging. Use the
[current scoring workflow](scoring.md) for the suite-aware SR report, particularly
for augmented variants.

Previous checked-in `viz_task_*.html` and `task*_viz.html` files were generated
snapshots, not website source. They remain recoverable from Git history; see the
[archive notes](../../analysis/archive/README.md). The actual game's HTML entry
points remain under `packages/client/`.
