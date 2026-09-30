# Scoring and result submission

Keep the model, harness, task suite, code revision, and trial count alongside every
result. Current repository verifiers are executable checks, not evidence that
every task criterion matches the paper perfectly. Protocol and verifier auditing
remain necessary for published comparisons.

## Success rate (SR)

```bash
python benchmarks/score.py --suite main \
  --trajectories runs/my-model/main/trial-1 \
  --output runs/my-model/main/trial-1/scores.json
```

Use `--suite augmented` for `data_v0.1_multi/v1.3_augmented`. The scorer reads
trajectories recursively and runs the checked-in task-specific `verify()`
functions. It does not trust a submitter's success flag or execute a verifier
from a path embedded in a submitted trajectory.

- `SR_percent` is populated only when every expected task has one valid result
  and no parsing/verification errors occurred.
- `observed_SR_percent` describes the scored subset only; it is not a full-suite
  score. Missing tasks are listed explicitly.
- Duplicate tasks, malformed JSON, empty trajectories, and verifier errors are
  reported as errors, not silently counted as task failures. The command exits
  nonzero for errors or when no trajectories can be scored.
- Score each trial separately. Do not combine repeated attempts in one directory
  or select only the best attempt. Record all trials and report the aggregation
  protocol when submitting results.

New runner outputs include `task_key` and `task_source`. Historical main logs with
only `task_id: task_NN` are supported. Augmented logs need an explicit task key or
source filename; an ID alone cannot distinguish the variants.

The runner now selects adjacent augmented verifiers for early stopping, and
uses the same selection logic as this scorer. Older augmented runs may have
stopped using main-task criteria; rescore and review those trajectories rather
than assuming their saved success flags remain comparable.

## Partial success rate (PSR)

A validated, portable implementation reproducing the paper's PSR is not present
in this upstream checkout. The separately maintained local experiment copy has
a reconstruction, but it has not been cross-validated against the historical
implementation. Do not label a replacement calculation as the published metric.
Report PSR as unavailable until its implementation and protocol are established.

## Causal contribution efficiency (CCE)

The existing analysis implementation is
`analysis/scripts/compute_cce_v2.py`. It uses an LLM judge; successful trajectories
require model API calls. Install its optional dependency separately:

```bash
python -m pip install -r analysis/requirements-cce.txt
export CCE_API_KEY='your-judge-api-key'
export CCE_BASE_URL='https://api.openai.com/v1'
export CCE_JUDGE_MODEL='gpt-4.1'
python analysis/scripts/compute_cce_v2.py \
  --trajectory runs/my-model/smoke/task_01_trajectory.json \
  --output runs/my-model/smoke/cce.json
```

This command retains the research script's CCE calculation. It reads
`metrics.task_verified_success` from the trajectory: verify that flag against the
matching task verifier before judging external or historical trajectories. A
failed trajectory receives zero CCE without judging its actions. Preserve judge
model/version, endpoint, prompt/protocol, and per-task output. Different judges
are different evaluation configurations, not interchangeable leaderboard scores.
The older `--model` / `--task` arguments remain for historical log layouts;
`AGENTWORLD_LOGS_DIR` overrides their log root.

## Submit through a GitHub issue

Use the website's [submission guide](https://agentworld.io/submission-guide) and
[Result submission issue form](https://github.com/openagents-org/agentworld-web/issues/new?template=result-submission.yml).
GitHub issues are the only result-submission route. Reviewers check the evidence
before results are published.

Include model ID/version, harness code and commit, benchmark/task revision,
configuration and prompts, trials/seeds, coverage, metric definitions, scores,
and downloadable raw trajectories/logs with checksums. Remove credentials from
configuration files before sharing them. Identify custom harnesses, changed
budgets, and alternative judges explicitly.
