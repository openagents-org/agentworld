# Manual game diagnostics

These scripts investigate specific game behaviors. They are not the benchmark
runner or offline unit tests.

| Script | Purpose |
| --- | --- |
| `test_attack_loot.py` | Log in a test character, fight mobs, inspect automatic loot collection |
| `test_harvest_resource.py` | Log in a test character, harvest resources, inspect inventory updates |
| `analyze_tile_data.py` | Inspect the checked-in map's resource/tile representation |

Paths are resolved from the script location, so no `/home/ubuntu` checkout is
required. Run from the repository root, for example:

```bash
python scripts/diagnostics/analyze_tile_data.py
```

The attack/harvest scripts act on a live game and alter test characters. Use a
dedicated test instance with the existing `TestAgent` accounts and set
`AGENTWORLD_BASE_URL` to its game API. For example:

```bash
AGENTWORLD_BASE_URL=http://localhost:7031 python scripts/diagnostics/test_attack_loot.py
```

For model experiments use [the benchmark quickstart](../../docs/benchmark/quickstart.md).
