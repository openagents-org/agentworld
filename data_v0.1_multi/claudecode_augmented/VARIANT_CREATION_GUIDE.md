# Benchmark Task Variant Creation Guide

This document describes the differences between Original, v1, and v2 variants of benchmark tasks, and provides guidelines for creating new variants.

---

## Executive Summary

Each benchmark task has **three versions**:
- **Original**: The baseline task configuration
- **v1**: "Easier" variant - more initial resources, reduced targets, fewer rounds
- **v2**: "Harder" variant - more rounds, increased targets, more agents, reduced starting materials

---

## Variant Philosophy

| Aspect | Original | v1 (Easier) | v2 (Harder) |
|--------|----------|-------------|-------------|
| **Design Goal** | Balanced baseline | Lower barrier to success | Test scalability & coordination |
| **Initial Resources** | Moderate | More pre-gathered materials | Less or no starting materials |
| **Target Quantities** | Standard | Reduced targets | Increased targets |
| **Time Limit** | Baseline rounds | Fewer rounds (task is simpler) | More rounds (task is larger) |
| **Agent Count** | Standard team | Same or fewer agents | Same or more agents |
| **Task Complexity** | Moderate | Simplified scope | Extended scope |

---

## Detailed Comparison by Task Type

### Type 1: Crafting Tasks (Tasks 00-05, etc.)

#### Pattern Observed:

| Version | max_action_steps | Initial Materials | Notes |
|---------|------------------|-------------------|-------|
| Original | 25 | None or minimal | Baseline difficulty |
| v1 | 30 | Pre-gathered key materials | Agents start with partial progress |
| v2 | 35 | None | More time but must gather everything |

#### Example: Task 01 - Magic Staff Crafting

| Version | Rounds | lumberjack logs | woodworker sticks | Key Difference |
|---------|--------|-----------------|-------------------|----------------|
| Original | 25 | 0 | 0 | Must gather all materials |
| v1 | 30 | 1 | 2 | 6 sticks worth pre-gathered (need 5) |
| v2 | 35 | 0 | 0 | More time, same requirements |

#### Example: Task 02 - Arrow Production

| Version | Rounds | Starting Logs | Total Feathers | Buffer |
|---------|--------|---------------|----------------|--------|
| Original | 35 | 0 | 10 (5+5) | Exact amount |
| v1 | 30 | 1 | 12 (6+6) | 2 extra feathers |
| v2 | 40 | 0 | 10 (5+5) | No buffer, more time |

---

### Type 2: Combat/Protection Tasks (Tasks 19-20, 50, etc.)

#### Pattern Observed:

| Version | Changes |
|---------|---------|
| Original | Standard combat objectives |
| v1 | Simplified objectives (fewer enemy types, reduced targets) |
| v2 | Extended objectives (more enemies, added agents for support) |

#### Example: Task 20 - Orchard Protection

| Version | Agents | Target Resources | Enemy Types | Rounds |
|---------|--------|------------------|-------------|--------|
| Original | 3 | 6 blueberry + 3 rawtuna | Wildlife + pests | 25 |
| v1 | 3 | 4 blueberry + 3 peach | Wildlife only (foraging only) | 20 |
| v2 | 4 | 8 blueberry + 5 rawtuna | Wildlife + pests (dual guardian) | 35 |

**v1 Changes:**
- Removed fishing requirement (easier skill set)
- Changed agent roles (both collectors are foragers)
- Reduced round count
- Added starting resources (1 blueberry, 1 peach)

**v2 Changes:**
- Added 4th agent (support guardian)
- Increased resource targets
- Extended round count
- Enhanced coordination requirements

#### Example: Task 50 - Elite Combat Battalion

| Version | Agents | Boss Tiers | Final Boss | Rounds |
|---------|--------|------------|------------|--------|
| Original | 5 | 4 | Spectre | 35 |
| v1 | 5 | 3 | Ogre | 30 |
| v2 | 6 | 5 | Ice Guardian | 45 |

**v1 Changes:**
- Removed Spectre (hardest boss)
- Reduced to 3-tier gauntlet
- Fewer rounds

**v2 Changes:**
- Added 6th warrior (DamageDealer2)
- Extended to 5-tier gauntlet
- Added Ice Guardian as final boss
- Enhanced stats for all agents
- More rounds and resources

---

### Type 3: Large-Scale Festival/Production Tasks (Tasks 80, 105, etc.)

#### Pattern Observed:

| Version | Agent Count | Production Targets | Complexity |
|---------|-------------|-------------------|------------|
| Original | 10 | Standard quotas | Full pipeline |
| v1 | 6 | Reduced quotas | Simplified pipeline |
| v2 | 12 | Increased quotas | Extended pipeline with more roles |

#### Example: Task 80 - Grand Festival Preparation

| Version | Agents | Phases | Food Items | Prizes | Decorations | Rounds |
|---------|--------|--------|------------|--------|-------------|--------|
| Original | 10 | 5 | 10+ | 4 | 3 | 51 |
| v1 | 6 | 4 | 8 | 3 | 0 | 38 |
| v2 | 12 | 4 | 25 | 7 | 4 | 55 |

**v1 Changes:**
- Reduced from 10 to 6 agents
- Removed decoration phase entirely
- Simplified production targets
- Consolidated roles (single cook, single forager)
- Slightly higher skill levels per agent

**v2 Changes:**
- Increased from 10 to 12 agents
- Added FestivalCoordinator and FestivalGuard roles
- Doubled most production targets
- Added coordinator with special items (beads)
- Extended rounds

#### Example: Task 105 - Legendary Golden Tribute

| Version | Agents | Gold Ore | Golden Bows | Golden Swords | Rounds |
|---------|--------|----------|-------------|---------------|--------|
| Original | 20 | 100 | 5 | 1 | 55 |
| v1 | 20 | 60 | 3 | 1 | 48 |
| v2 | 20 | 140 | 7 | 2 | 70 |

**v1 Changes:**
- Reduced production targets (60% of original)
- Miners start with 3 goldore each (30 total head start)
- Hunters start with logs (2 each)
- Higher skill levels (+5 across the board)
- More coal per smith (50 vs 40)
- Fewer rounds but easier targets

**v2 Changes:**
- Increased production targets (140% of original)
- No starting goldore
- Lower skill levels (-2 across the board)
- Less coal per smith (35 vs 40)
- More rounds to compensate
- Added second hilt for 2 swords

---

## Variant Creation Guidelines

### Creating v1 (Easier Variant)

1. **Add Starting Materials**
   - Give agents 20-50% of required materials pre-gathered
   - Focus on bottleneck materials (e.g., rare ores, key components)

2. **Reduce Targets**
   - Lower quantity requirements by 30-50%
   - Simplify multi-step objectives

3. **Adjust Rounds**
   - Often FEWER rounds (task is simpler)
   - Or same rounds with easier path to completion

4. **Simplify Scope**
   - Remove optional/bonus objectives
   - Focus on core task completion
   - May remove entire phases (e.g., decoration phase)

5. **Boost Agent Capabilities**
   - Increase skill levels by 2-5 points
   - Add more consumables (flasks, apples)
   - Better starting equipment if applicable

### Creating v2 (Harder Variant)

1. **Remove Starting Materials**
   - Agents start with nothing or minimal supplies
   - Remove safety buffers (exact materials needed)

2. **Increase Targets**
   - Raise quantity requirements by 30-50%
   - Add additional objectives

3. **Extend Rounds**
   - MORE rounds to handle increased scope
   - Typically +20-40% more rounds

4. **Scale Up Complexity**
   - Add more agents with specialized roles
   - Introduce additional phases
   - Add more enemy tiers or harder bosses

5. **Adjust Agent Capabilities**
   - Slightly lower skill levels (-2 to -5 points)
   - Fewer consumables
   - Requires better coordination

---

## Summary Table: All Variant Dimensions

| Dimension | v1 Direction | v2 Direction |
|-----------|--------------|--------------|
| Starting materials | MORE | LESS |
| Target quantities | LOWER | HIGHER |
| Round limit | Often LOWER | HIGHER |
| Agent count | Same or FEWER | Same or MORE |
| Skill levels | HIGHER | Same or LOWER |
| Consumables | MORE | Same or LESS |
| Phases/complexity | SIMPLIFIED | EXTENDED |
| Enemy count (combat) | FEWER | MORE |
| Safety buffers | YES | NO |

---

## File Naming Convention

```
task_XX_task_name.yaml      # Original
task_XX_task_name_v1.yaml   # Easier variant
task_XX_task_name_v2.yaml   # Harder variant
```

---

## Header Comments

Each variant file should include a header comment explaining the variant:

```yaml
# AgentWorld Multi-Agent Task Configuration
# VARIANT: v1 - More initial resources, easier completion

# or

# AgentWorld Multi-Agent Task Configuration
# VARIANT: v2 - More rounds, adjusted resources
```

---

## Verification Checklist

Before finalizing a variant:

- [ ] Header comment clearly indicates variant type
- [ ] max_action_steps adjusted appropriately
- [ ] Inventory items modified per variant guidelines
- [ ] Skill levels adjusted if needed
- [ ] Success criteria updated to match new targets
- [ ] Task description/context updated if scope changed
- [ ] Agent count matches variant design
- [ ] All resource math is correct (enough materials to complete)
