# Legacy utilities

`batch_verify.sh` is the historical batch wrapper around the root
`task_verifier.py`. Its scoring behavior is preserved for reproducing old work;
use [benchmarks/score.py](../../benchmarks/score.py) for the current offline SR workflow.

```bash
bash scripts/legacy/batch_verify.sh path/to/old/logs runs/legacy-results.csv
```

Create the output's parent directory first. Input and output paths are relative
to your working directory; the script locates its Python verifier relative to
the repository. The historical verifier is not an augmented-suite selector.
