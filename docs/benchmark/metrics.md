# Evaluation metrics

This document specifies the checkpoint PSR reconstruction used for the September
2026 additional-model experiments, alongside SR, CCE, Rounds, and Chats.
The implementation is [scripts/score_psr.py](../../scripts/score_psr.py), with
offline [regression tests](../../tests/benchmark/test_psr.py).

**Reproducibility boundary:** this is method `checkpoint_fraction_v1`. It
reconstructs the paper's verbal checkpoint definition, but has not been
cross-validated against the unavailable historical PSR program. Label its output
**reconstructed PSR**, rather than claiming it reproduces every published PSR
value. It uses fractional credit for numeric quantities; it is not the proportion
of checkpoints whose targets have been fully met.

## Partial success rate (PSR)

For task *i* with *Kᵢ* verifier checkpoints, assign each checkpoint a credit:

| Checkpoint | Credit | Example |
| --- | --- | --- |
| Quantity with target *r* and observed amount *a* | `min(a / r, 1)` | `Logs: 3/5` → 0.6 |
| Boolean condition | 1 for `True`, 0 for `False` | `All alive: True` → 1 |
| Upper bound on rounds | 1 if `actual <= limit`, otherwise 0 | `Rounds: 30/25` → 0 |

The per-task score is:

```text
PSR_i = 1                                      if the task verifier reports success
        (credit_i1 + ... + credit_iK) / K_i     otherwise

PSR_percent = 100 × (PSR_1 + ... + PSR_N) / N
```

Each checkpoint has equal weight within its task, and each task has equal weight
within a reported split. We do not pool all checkpoints across tasks: a task with
more checkpoints does not receive more weight. A successful task receives 1 even
if its diagnostic message omits checkpoints or describes intermediate states.

For example, for an unsuccessful task with this verifier message:

```text
Logs: 3/5, Kills: 0/3, All alive: True
```

the checkpoint credits are 0.6, 0, and 1. Its PSR is `(0.6 + 0 + 1) / 3`, or
**53.33%**, while its binary success score is 0. If another task succeeds, the
two-task mean PSR is **76.67%** and SR is **50%**.

The script reads comma-separated `label: value` messages from the verifier.
Numeric targets normally appear as `actual/target`. For legacy messages that
omit a denominator, the explicit `BARE_TARGETS` table in the script supplies
targets taken from the corresponding verifier predicates. Unknown formats,
unknown bare targets, and nonpositive targets raise errors; they are not replaced
with zero. If a verifier changes its message or criteria, review this mapping
and version the scoring protocol before comparing results.

## Task success rate (SR)

```text
SR_percent = 100 × number of successful tasks / number of tasks
```

For new runs, [benchmarks/score.py](../../benchmarks/score.py) calls the checked-in
task-specific verifiers. See the [scoring guide](scoring.md) for commands.

The historical additional-model collector in `scripts/score_psr.py` deliberately
uses [task_verifier.py](../../task_verifier.py): version 0 for Main, version 1 for
`_v1`, and version 2 for `_v2`. This preserves that experiment's verifier choice.
It does **not** silently switch historical results to the newer adjacent-task
verifier path in `benchmarks/score.py`. Record the verifier and code revision;
these paths are not certified equivalent. For augmented results, do not trust a
saved main-task success flag without verifying the variant.

## Causal Collaboration Effectiveness (CCE)

[compute_cce_v2.py](../../analysis/scripts/compute_cce_v2.py) first asks an LLM
judge which actions directly achieved the objective. It then traces backward by
round to identify actions that enabled contributing actions in later rounds.
The union of those actions is the contributing set *C*.

```text
CCE_i = |C_i| / |T_i|     for a successful task with recorded actions
        0                 for a failed task or a task with no recorded actions

CCE = (CCE_1 + ... + CCE_N) / N
```

`T` contains the nonempty action strings extracted from the trajectory. The
implementation rounds each per-task CCE to four decimal places before saving
`ce`; the experiment summary averages these saved values. The reported mean
includes failed tasks with zero CCE. It is neither a successful-task-only mean
nor a ratio formed by pooling action counts across tasks.

CCE requires a configured judge API for successful tasks; PSR does not use an
LLM. See the [CCE commands](scoring.md#causal-collaboration-effectiveness-cce).
Keep the judge model/version, prompts, endpoint, and per-task output with the
results. The additional-model experiments used Vertex Gemini 2.5 Flash; the
paper's original table used GPT-4.1. Scores from different judges must be labeled
and are not directly interchangeable. A judge/API failure is a pending score,
not a model failure or a zero CCE.

## Rounds and Chats

These are arithmetic task means of the trajectory's `metrics.total_rounds` and
`metrics.total_chats`, respectively, including valid failed tasks. They are not
per-agent means. Report Main Rounds/Chats when reproducing the table layout used
for the additional-model experiments.

## Run the PSR script

Python 3.10+ is sufficient; this script uses only the standard library and the
repository verifier. Run commands from the repository root.

### From checkpoint inputs

The input JSON maps model names to task rows. Every row has `stage` (`main` or
`augmented`), the full task filename stem, boolean `success`, verifier `message`,
saved `CCE` in [0, 1], and nonnegative `rounds` and `chats`. For example:

```json
{
  "example-model": [
    {
      "stage": "main",
      "task": "task_01_magic_staff",
      "success": false,
      "message": "Logs: 3/5, Kills: 0/3, All alive: True",
      "CCE": 0.0,
      "rounds": 30,
      "chats": 8
    }
  ]
}
```

This is a synthetic parser example, not task 01's actual verifier output. Save
it as `runs/checkpoint-inputs.json`, then run:

```bash
python scripts/score_psr.py runs/checkpoint-inputs.json runs/psr-results.json
```

The command writes the inputs back to the input path and writes the full report
to the output path. Use separate paths and copies if you want to preserve an
earlier input snapshot. The result includes per-checkpoint credits, per-task PSR,
the method ID, `historical_implementation_reproduced: false`, and split summaries.

### From the audited additional-model result layout

The collector supports any model directory name and both original and copied
result trees:

```text
RESULTS_ROOT/MODEL/main/TASK/completed.json
RESULTS_ROOT/MODEL/main/TASK/cce.json
RESULTS_ROOT/MODEL/main/TASK/ATTEMPT/task_NN_trajectory.json
RESULTS_ROOT/MODEL/augmented/TASK_v1/...  (or TASK_v2)
```

```bash
python scripts/score_psr.py runs/checkpoint-inputs.json runs/psr-results.json \
  --collect-root . \
  --results-root /path/to/additional-model-results
```

`--collect-root` selects the repository's verifier and task catalog. Without
`--results-root`, collection retains the historical default
`agents/logs/additional_20260925` under that repository. The collector prefers the
sibling attempt trajectory in a copied folder over the original absolute path
stored in a completion marker. It re-verifies outcomes, checks task identity and
marker metrics, and requires agreement with saved CCE success. Cached rows are
invalidated when the completion marker, CCE record, verifier, or trajectory changes.

This collector requires `completed.json` and `cce.json`, which were produced by
the additional-model experiment harness. It does not discover arbitrary raw
runner outputs or generate CCE scores. A missing CCE file leaves that task out
of the collected rows, so its PSR/SR summaries are also partial until scoring
finishes. The collector is not a replacement for initialization and trace audits.

### Coverage and reporting

- Main has 100 tasks; Augmented v1 and v2 have 100 each; their union has 200.
- The script checks task identities against the repository YAML catalog and
  rejects duplicate rows, unexpected tasks, and invalid numeric metrics.
- Every summary includes `scored`, `expected`, `missing_tasks`, and `final`.
  When `final` is false, numeric means describe only the scored subset. Do not
  present them as complete benchmark scores or impute missing tasks as zero.
- Audit complete team initialization, initial observations, inference failures,
  and one selected valid attempt per task before collection. Preserve interrupted
  attempts; infrastructure failures remain pending rather than model failures.
- Score trials separately and state the trial aggregation policy. Do not select
  the best attempt or pool repeated trials as if they were distinct tasks.
- Report Main, v1, and v2 separately. The additional-model v1 split is not
  established as equivalent to the original paper's historical augmented subset.

Run the offline regression tests with:

```bash
python -m unittest discover -s tests/benchmark -p 'test_psr.py' -v
```
