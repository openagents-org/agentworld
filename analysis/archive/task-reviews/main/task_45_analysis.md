# Task 45 - Caravan Escort Analysis

## Task Summary

**Task Name:** Caravan Escort - Protected Gathering
**Description:** Three agents protect a gatherer while they collect valuable resources

**Objectives:**
- Miner (agent_3) collects 3+ Gold Ore (goldnugget)
- Guards (agent_1, agent_2) defeat at least 2 hostile creatures
- All agents survive the escort mission

**Agent Configuration:**
| Agent | Role | Location | Key Skills | Equipment |
|-------|------|----------|------------|-----------|
| agent_1 (t45_guard1_agent) | Guard (Melee) | (225, 45) | Strength 40, Defense 35, Health 50 | Sword, Plate Armor |
| agent_2 (t45_guard2_agent) | Guard (Ranged) | (240, 45) | Archery 35, Accuracy 40 | Wooden Bow, 40 Arrows |
| agent_3 (t45_miner_agent) | Miner | (232, 45) | Mining 30 | Pickaxe |

---

## Verification Result

**Status: FAILED**

| Criteria | Verifier Output | Actual Reality | Assessment |
|----------|-----------------|----------------|------------|
| Gold Ore | 13/3 | 17 harvests, 13 retained by miner | PASS |
| Kills | 0/2 | 6 kills (Spectre x1, Preta x4, Iron Ogre x1) | **VERIFIER BUG** |
| All Alive | True | False (agent_1 died to Ogre Lord) | **VERIFIER BUG** |

**Task Verification Message:** `"Miner gold ore: 13/3, Kills: 0/2, All alive: True"`

---

## Root Cause Analysis

### Primary Failure: VERIFIER BUGS (Not LLM or Game Design Error)

The task **SHOULD have failed correctly** but the verifier outputs are wrong:
- **Gold collection: PASS** - Miner collected 17 gold ore (13 retained after transfers)
- **Combat kills: Actually 6 kills** - But verifier shows 0
- **All alive: Actually FALSE** - agent_1 died with HP=0, but verifier shows True

### Bug 1: Kill Counter Not Detecting Kills

The `count_combat_kills()` function looks for kill indicators in `json.dumps(obs).lower()` and mobs with `hitPoints=0`. However, the "VICTORY: Defeated..." messages are in the **tool result string**, not in the observation JSON. The killed mob despawns before the observation is recorded.

**Evidence - Actual kills that occurred:**
| Round | Agent | Target |
|-------|-------|--------|
| 4 | agent_1 | Spectre (Lv32) |
| 6 | agent_1 | Preta (Lv36) |
| 8 | agent_1 | Preta (Lv36) |
| 14 | agent_1 | Preta (Lv36) |
| 15 | agent_1 | Preta (Lv36) |
| 25 | agent_3 | Iron Ogre (Lv20) |

### Bug 2: HP Tracking Reports "All Alive: True" Despite Death

The trajectory clearly shows agent_1 with `hitPoints: 0` at round 22, but verifier reported all alive.

### Secondary Issue: LLM Decision Failure (Fatal Engagement)

agent_1 attacked **Ogre Lord (Level 44, 2850 HP)** - a boss mob significantly stronger than the agent. agent_1 was slain after 87 seconds of combat.

---

## Timeline of Key Events

| Time | Round | Event |
|------|-------|-------|
| 18:14 | 0 | Agents spawned in mountain region |
| 18:31 | 4 | agent_1 defeats Spectre (1st kill) |
| 18:36 | 6 | agent_1 defeats Preta (2nd kill) |
| 19:00 | 8 | agent_1 defeats Preta (3rd kill) |
| 20:01 | 14 | agent_1 defeats Preta (4th kill) |
| 20:08 | 15 | agent_1 defeats Preta (5th kill) |
| **21:40** | **22** | **agent_1 attacks Ogre Lord and is SLAIN (HP: 0/1569)** |
| 22:24 | 25 | agent_3 defeats Iron Ogre (6th kill) |
| 22:50 | 33 | Task ends with miner holding 13 gold ore |

---

## Conclusion

### Classification: **VERIFIER BUG** (Primary) + **LLM Decision Failure** (Secondary)

**What actually happened:**
1. **Gold ore: 13/3** - PASS
2. **Kills: 6/2** - PASS (but verifier shows 0)
3. **All alive: False** - FAIL (agent_1 died, but verifier shows True)

### Recommendations

1. **Fix Kill Counter:** Check for "VICTORY" messages in tool results, not just observation JSON
2. **Fix HP Tracking:** Debug why `get_final_agent_hp_simple()` returned all agents alive when trajectory clearly shows HP=0
3. **Optional Task Improvement:** Add explicit warning about Ogre Lord boss in the task context
