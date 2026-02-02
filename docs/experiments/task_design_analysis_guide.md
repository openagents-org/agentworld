# Task Design Analysis & Fix Guide

This document describes the methodology for analyzing and fixing task design problems in the v1.3 benchmark. Use this as a reference when diagnosing why tasks fail.

---

## Table of Contents

1. [Failure Classification](#failure-classification)
2. [Investigation Methodology](#investigation-methodology)
3. [Common Task Design Issues](#common-task-design-issues)
4. [Fix Patterns](#fix-patterns)
5. [Case Studies](#case-studies)
6. [Data Files Reference](#data-files-reference)

---

## Failure Classification

When a task fails, first classify the failure type:

### Task Design Issues (Fixable)
- **Wrong spawn location** - Agents spawned far from required resources
- **Wrong resource type** - Resource at location gives different item than expected
- **Boss not found** - Boss doesn't exist at specified coordinates
- **Item ID mismatch** - Task uses wrong item key (e.g., `goldore` vs `goldnugget`)

### Agent Behavior Issues (Not task design)
- **Crafting failed despite materials** - Agents collected resources but didn't craft
- **No actions executed** - Agents talked but didn't act
- **Coordination breakdown** - Multi-agent handoff failed

---

## Investigation Methodology

### Step 1: Check Trajectory Logs

Look at the trajectory file to understand what agents actually did:

```bash
# Find trajectory file
ls agents/logs/v1.3_*/task_XX_trajectory.json

# Check what resources were collected
python3 -c "
import json
d = json.load(open('path/to/trajectory.json'))
print('Rounds:', d.get('metrics', {}).get('total_rounds'))
print('Actions:', d.get('metrics', {}).get('total_actions'))
"
```

### Step 2: Check Screen/Task Runner Logs

Look for harvest/mining activity:

```bash
# Check if agents harvested the right resources
grep -E "HARVEST COMPLETE|Mining|harvested" agents/logs/v1.3_*/screen*.log

# Check what item was obtained
grep -E "ironore|nisocore|goldnugget|goldore" agents/logs/v1.3_*/task_runner_*.log
```

### Step 3: Verify Resource Locations

Check game data files to find where resources actually spawn:

```bash
# For rocks/ores - check rocks.json
cat packages/server/data/rocks.json | python3 -c "
import json, sys
rocks = json.load(sys.stdin)
for name, data in rocks.items():
    print(f'{name}: gives {data.get(\"item\")}, requires level {data.get(\"levelRequirement\")}')"

# For rock locations - parse world.json
# Iron Rock tile ID: 1392
# Find coordinates with that tile
```

### Step 4: Verify Boss Locations

Check mob spawn data:

```bash
# Check mobs.json for boss stats
cat packages/server/data/mobs.json | python3 -m json.tool | grep -A5 "skeleton\|wizard\|mermaid"

# Check spawn areas in world data
cat packages/server/data/map/world.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
# Look for mob spawn areas
"
```

---

## Common Task Design Issues

### Issue 1: Wrong Ore/Rock Location

**Symptom:** Task requires `ironore` but agents collect 0, or collect wrong item like `nisocore`.

**Root Cause:** Different rock types give different ores:
| Rock Type | Item Dropped | Location |
|-----------|--------------|----------|
| Iron Rock | `ironore` | (545-600, 492-635) |
| Nisoc Rock | `nisocore` | (336, 5) area |
| Ibo Rock | `iboore` | Various |
| Gold Rock | `goldnugget` | (141, 5) area |
| Coal Rock | `coal` | Various |

**Fix:**
1. Update agent spawn coordinates in YAML to actual rock location
2. Add ORE TYPE REFERENCE to `relevant_game_context`

**Example Fix (Iron Ore):**
```yaml
# BEFORE - Wrong location
agent_1:
  location:
    x: 336
    y: 5

# AFTER - Correct iron rock location
agent_1:
  location:
    x: 545
    y: 495
```

### Issue 2: Item ID Mismatch

**Symptom:** Task objective uses wrong item key.

**Common Mistakes:**
| Wrong | Correct | Notes |
|-------|---------|-------|
| `goldore` | `goldnugget` | Gold rocks drop nuggets, not ore |
| `logs` | `willowlogs`, `palmlogs` | Different tree types |
| `ore` | `ironore`, `nisocore` | Be specific |

**Fix:** Update task objectives and `relevant_game_context` with correct item keys.

### Issue 3: Boss Not Found

**Symptom:** Combat task fails with 0 kills despite fighters being present.

**Investigation:**
1. Check if boss spawns at specified coordinates
2. Verify boss respawn timer hasn't expired
3. Check if boss name matches game data

**Common Boss Locations (verify in game data):**
- Skeleton: Check dungeon/cave areas
- Ancient Wizard: Check tower/magic areas
- Mermaid: Check coastal/water areas
- Hermit Crab: Check beach areas

**Fix:** Update fighter spawn coordinates to actual boss location.

### Issue 4: Resource Not at Spawn Location

**Symptom:** Agents at location but resource count is 0.

**Investigation:**
1. Check if resource type exists at location
2. Verify resource respawn rate
3. Check if location is accessible (not blocked)

---

## Fix Patterns

### Pattern 1: Update Spawn Coordinates

```yaml
# Update location for agents that need the resource
agent_X:
  location:
    x: NEW_X  # Coordinates where resource actually exists
    y: NEW_Y
```

### Pattern 2: Add Resource Reference to Context

```yaml
relevant_game_context: |
  ...existing context...

  ORE TYPE REFERENCE (important - different rocks give different ores):
  - Iron Rock (around 545, 495): gives "ironore" (requires mining level 10)
  - Nisoc Rock (around 336, 5): gives "nisocore" (NOT iron!)
  - Gold Rock (around 141, 5): gives "goldnugget" (NOT "goldore")

  LOCATIONS:
  - Iron Ore Mining: Around (545, 495) - THIS IS WHERE IRON ROCKS ARE
```

### Pattern 3: Fix Item Keys in Objectives

```yaml
# BEFORE
objectives:
  primary: Collect 6x goldore

# AFTER
objectives:
  primary: Collect 6x goldnugget (from gold rocks)
```

### Pattern 4: Add Username Prefixes for Parallel Runs

To avoid login conflicts when running multiple tasks in parallel:

```bash
# Add task-specific prefix to all usernames
sed -i "s/username: /username: t${task_num}_/g" task_file.yaml
```

---

## Case Studies

### Case Study 1: Iron Ore Location Fix (Batch 3)

**Problem:** 8 tasks (78, 82, 84, 86, 87, 93, 98, 100) all collected 0 iron ore.

**Investigation:**
1. Checked trajectory logs - agents were mining but getting `nisocore`
2. Examined `rocks.json` - found iron rocks give `ironore`, nisoc rocks give `nisocore`
3. Parsed `world.json` for tile ID 1392 (iron rock) - found at (545-600, 492-635)
4. Original spawn location (336, 5) had Nisoc rocks, not Iron rocks

**Fix Applied:**
1. Updated miner spawn coordinates from (336, 5) → (545, 495)
2. Added ORE TYPE REFERENCE to all task YAML files
3. Fixed `goldore` → `goldnugget` in task 78

**Results:**
- Before: 0 iron ore harvested across all tasks
- After: 520 iron ore harvested
- 2 tasks converted from FAIL → PASS (82, 98)
- 6 tasks still failed due to secondary objectives (crafting/combat)

**Key Files Modified:**
- `task_78_trading_network.yaml`
- `task_82_evacuation.yaml`
- `task_84_tunnel_expedition.yaml`
- `task_86_forge_vanguard.yaml`
- `task_87_canal_restoration.yaml`
- `task_93_fortress_construction.yaml`
- `task_98_mining_conglomerate.yaml`
- `task_100_resource_survey.yaml`

### Case Study 2: Boss Location Issues (Pending)

**Problem:** Tasks 84, 90, 91, 95, 99 fail combat objectives.

**Identified Issues:**
- Task 84: Skeletons not defeated (fighters at 238, 48 - wrong location?)
- Task 90: Ancient Wizard not found
- Task 91: Hermit Crab not found (Iron Ogre and Ogre Guardian found)
- Task 95: Mermaid not defeated
- Task 99: Ancient Wizard not found

**Next Steps:**
1. Find actual spawn coordinates for each boss type
2. Update fighter spawn locations in task YAML files
3. Re-run affected tasks

---

## Data Files Reference

### Game Data Files

| File | Purpose | Location |
|------|---------|----------|
| `rocks.json` | Rock types and items dropped | `packages/server/data/rocks.json` |
| `mobs.json` | Monster stats and drops | `packages/server/data/mobs.json` |
| `world.json` | Map tile data, spawn locations | `packages/server/data/map/world.json` |
| `items.json` | Item definitions | `packages/server/data/items.json` |

### Task YAML Structure

```yaml
task:
  name: Task Name
  description: Brief description
objectives:
  primary: What needs to be accomplished
relevant_game_context: |
  Instructions and context for agents
max_action_steps: 55
agent_1:
  username: unique_agent_name
  new_character: true
  location:
    x: X_COORD
    y: Y_COORD
  skill_levels:
    mining: 40
  inventory_items:
    - item: flask
      count: 20
  equipped_items:
    - item: pickaxe
      count: 1
success_criteria:
  - Condition 1
  - Condition 2
```

### Useful Commands

```bash
# Find rock locations by tile ID
python3 -c "
import json
world = json.load(open('packages/server/data/map/world.json'))
# Parse tiles to find specific tile IDs
"

# Check rock types
cat packages/server/data/rocks.json | python3 -m json.tool

# Find boss spawn areas
grep -r "skeleton\|wizard\|mermaid" packages/server/data/

# Run task with username prefix to avoid conflicts
sed -i 's/username: /username: tXX_/g' task_file.yaml
```

---

## Checklist for New Task Fixes

- [ ] Identify failure type (task design vs agent behavior)
- [ ] Check trajectory logs for actual agent actions
- [ ] Verify resource/boss locations in game data
- [ ] Update spawn coordinates if needed
- [ ] Add resource type reference to `relevant_game_context`
- [ ] Fix any item ID mismatches
- [ ] Add username prefix if running in parallel
- [ ] Re-run task and verify fix
- [ ] Update results documentation

---

## Related Documents

- [v1.3_benchmark_results.md](v1.3_benchmark_results.md) - Full benchmark results
- Task YAML files: `data_v0.1_multi/v1.3_benchmark/task_*.yaml`
- Log directories: `agents/logs/v1.3_*/`
