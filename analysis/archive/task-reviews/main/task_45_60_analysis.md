# Task 45-60 Failure Analysis

## Summary

| Task | Task Name | Status | Fixed | Understood |
|------|-----------|--------|-------|------------|
| 45 | Caravan Escort | FAIL | [x] | [x] |
| 46 | Mining Expedition | SUCCESS | - | - |
| 47 | Magic Staff Forge | FAIL | [ ] | [x] |
| 48 | Cross-Region Expedition | FAIL | [x] | [x] |
| 49 | Jewelry Workshop | FAIL | [x] | [x] |
| 50 | Combat Battalion | FAIL | [x] | [x] |
| 51 | Survival Challenge | FAIL | [x] | [x] |
| 52 | Smithy Operation | FAIL | [x] | [x] |
| 53 | Culinary Expedition | SUCCESS | [x] | [x] |
| 54 | Archery Academy | FAIL | [x] | [x] |
| 55 | Boss Raid | FAIL | [ ] | [ ] |
| 56 | Cross-Region Trading | FAIL | [ ] | [x] |
| 57 | Grand Jewelry Expedition | FAIL | [ ] | [x] |
| 58 | Harvest Festival | FAIL | [x] | [x] |
| 59 | Elite Merchant Guild | FAIL | [ ] | [ ] |
| 60 | Mining Operation | SUCCESS | - | - |

---

## Detailed Analysis

### Task 45 - Caravan Escort
- **Status:** FAIL
- **Verification (Latest - 2026-02-01):** Miner gold ore: 13/3 ✅, Kills: 4/2 ✅, All alive: False ❌
- **Root Cause:** **MULTIPLE BUGS - Verifier Bugs + Game Design Issue (Dangerous Spawn Area)**

  **Latest Run Analysis (rerun_45_60_20260201_181412):**
  
  | Criteria | Result | Details |
  |----------|--------|---------|
  | Gold Ore | ✅ 13/3 | Miner successfully collected 13 gold ore |
  | Kills | ✅ 4/2 | Guards killed: Spectre, Dark Mage, Preta, Iron Ogre |
  | All Alive | ❌ False | Agent_1 (guard1) was slain by **Ogre Lord (Level 44)** |

  ---

  **Bug 1: Verifier `get_final_agent_hp_simple` Only Checked Last Round (CRITICAL)**
  - Function only checked the LAST round for agent HP
  - Dead agents don't take actions in subsequent rounds → missing from last round
  - Result: Dead agent_1 was not in round 33, so HP check only saw agent_3
  - `all(hp > 0 for hp in {'agent_3': 779}.values())` = True (WRONG!)
  
  **Fix Applied to `verifier_utils.py`:**
  ```python
  # Old (broken) - only checked last round
  last_round = traj_json['rounds'][-1]
  for act in last_round.get('actions', []):
      # Only sees agents who took actions in final round
  
  # New (fixed) - tracks HP across ALL rounds
  for r in traj_json.get('rounds', []):
      for act in r.get('actions', []):
          # Track last known HP for each agent
          # Also checks observation.playerStatus.hitPoints
  ```

  ---

  **Bug 2: Verifier `count_combat_kills` Pattern Matching Was Broken (CRITICAL)**
  - Old function looked for patterns like "hostile", "creature" in **action strings**
  - But actions look like: `attack_entity(targetInstance=123456)` - no mob name!
  - Also checked for "dead"/"killed" in observation, but game uses different terminology
  
  **Fix Applied to `verifier_utils.py`:**
  ```python
  # Old (broken) - looked for patterns in action string
  if pattern.lower() in action_str:  # Never matched!
  
  # New (fixed) - checks mobs array in observation for HP=0
  mobs = obs.get('mobs', [])
  for mob in mobs:
      if mob.get('hitPoints', -1) == 0:
          kills += 1  # Track by instance ID to avoid double counting
  ```

  ---

  **Bug 3: Task 45 Verifier Used Wrong Kill Patterns**
  - Called: `count_combat_kills(traj_json, ['hostile', 'creature', 'enemy', 'monster'])`
  - Actual mob names: "Spectre", "Dark Mage", "Preta", "Iron Ogre" - no pattern match!
  
  **Fix Applied to `task_45_success_criteria.py`:**
  ```python
  # Old (broken)
  kills = count_combat_kills(traj_json, ['hostile', 'creature', 'enemy', 'monster'])
  
  # New (fixed) - count ALL mob kills
  kills = count_combat_kills(traj_json, None)
  ```

  ---

  **Game Design Issue: Dangerous Spawn Location**
  - Gold Rocks are located in a high-level area with dangerous mobs
  - Agent_1 (guard1) attacked **Ogre Lord (Level 44, 2850 HP)** - a boss mob!
  - Guard1 had decent stats but was no match for a boss → slain in combat
  - This caused "All alive: False" despite good gold collection and kills

  **Evidence from trajectory:**
  ```json
  // Agent_1's final observation shows HP=0
  "playerStatus": {
    "name": "t45_guard1_agent",
    "hitPoints": 0,
    "maxHitPoints": 1569
  }
  
  // Mobs in area included Ogre Lord (boss)
  "mobs": [{
    "name": "Ogre Lord",
    "level": 44,
    "hitPoints": 1753,
    "maxHitPoints": 2850
  }]
  ```

  ---

  **Historical Bugs (Fixed Earlier):**
  
  **Bug 4: Verifier Used Wrong Username**
  - Verifier looked for: `agent_items.get('miner_agent', {})`
  - Actual agent key: `agent_3`
  - ✅ Fixed: Now uses `agent_items.get('agent_3', {})`

  **Bug 5: Verifier Used Wrong Item Key**
  - Verifier looked for: `miner_items.get('goldore', 0)`
  - Actual item key from mining: `goldnugget`
  - Both display as "Gold Ore" but have different internal keys!
  - ✅ Fixed: Now uses `miner_items.get('goldnugget', 0)`

  **Game has TWO items both named "Gold Ore":**
  | Item Key | Display Name | Source | Used For |
  |----------|--------------|--------|----------|
  | `goldnugget` | "Gold Ore" | Mining Gold Rock | Smithing → goldbar (no coal needed) |
  | `goldore` | "Gold Ore" | **NOTHING - orphaned item!** | Smelting → goldbar (requires coal) |

  **Bug 6: Task YAML Used Wrong Item Key `goldore`**
  - Task description referenced non-existent `goldore` in 3 places
  - ✅ Fixed in `task_45_caravan_escort.yaml`:
  
  | Location | Before | After |
  |----------|--------|-------|
  | objectives.primary | `3x goldore` | `3x Gold Ore (goldnugget)` |
  | relevant_game_context (TARGETS) | `3x goldore` | `3x Gold Ore (itemKey: goldnugget)` |
  | success_criteria | `3x goldore` | `3x goldnugget (Gold Ore)` |

- **Category:** Verifier Bug + Task Definition Bug + Game Design Issue (dangerous spawn area)
- **Fixes Applied:**
  1. ✅ `get_final_agent_hp_simple` now tracks HP across ALL rounds
  2. ✅ `count_combat_kills` now checks mob HP=0 in observations
  3. ✅ Task 45 verifier uses `None` for kill patterns (count all kills)
  4. ✅ Verifier uses `agent_3` instead of username
  5. ✅ Verifier uses `goldnugget` instead of `goldore`
  6. ✅ Task YAML updated: `goldore` → `goldnugget` in all references
  7. [ ] Consider relocating spawn away from Ogre Lord boss area
- **Fixed:** [x] (all verifier and task definition bugs fixed)
- **Understood:** [x]

---

### Task 46 - Mining Expedition
- **Status:** SUCCESS
- **Verification:** Pickaxe: 1/1, Axe: 1/1, Heavy Sword: 1/1
- **Root Cause:** -

---

### Task 47 - Magic Staff Forge
- **Status:** FAIL
- **Verification:** Lightning Staff: 1/2, Fire Staff: 1/1
- **Root Cause:** **LLM Attention/Reasoning Failure (NOT data visibility)**
  
  **What happened:**
  - crafter1 (agent_4) successfully crafted 1st lightning staff
  - After crafting, inventory clearly showed: `staff x1` + `lightningbead x1` (enough for 2nd!)
  - Instead of crafting 2nd lightning staff, agent started chatting asking for more sticks
  - Agent never called `craft_item(lightningstaff)` again despite having materials
  - Kept asking for firebead (already used by crafter2) until task timed out
  
  **Key insight - LLM DID see the inventory:**
  - System prompt is refreshed with `observe_environment()` BEFORE every API call
  - Observation JSON included inventory: `{"lightningbead": 1, "staff": 1, "stick": 6}`
  - The LLM **saw the inventory but didn't reason about it correctly**
  - This is an attention/reasoning failure, not missing information
  
  **Evidence from trajectory (lines 34647-34690):**
  ```json
  "inventory": {
    "items": [
      {"key": "lightningstaff", "count": 1},
      {"key": "lightningbead", "count": 1},  // HAD 1 MORE!
      {"key": "staff", "count": 1},          // HAD BASE STAFF!
      {"key": "stick", "count": 6}
    ]
  }
  ```
  
  **LLM failure pattern:** Fell back to earlier conversation patterns (when it actually needed materials) instead of checking current state.

- **Category:** LLM attention failure - ignored visible inventory data
- **Fixed:** [ ]
- **Understood:** [x]

---

### Task 48 - Cross-Region Expedition
- **Status:** FAIL
- **Verification:** Logs: 1/5, Coal: 0/4, Shrimp: 0/3
- **Root Cause:** **LLM Hallucination - transferred to WRONG player (from different task)**

  **What happened:**
  - Task 48 has 5 agents: `t48_forest1_agent`, `t48_forest2_agent`, `t48_mountain1_agent`, `t48_mountain2_agent`, `t48_coastal_agent`
  - Task instructions said "Transfer items to coordinator when done" but **NO coordinator was defined** in task 48
  - Task 54 (running in parallel) has an agent named `t54_coordinator_agent`
  - The LLM hallucinated and transferred items to `t54_coordinator_agent` instead of a teammate
  
  **Evidence from logs:**
  ```
  20:44:59 - Transfer completed: 5x Logs transferred to t54_coordinator_agent  ← WRONG!
  20:47:51 - Transfer completed: 4x Coal transferred to t54_coordinator_agent  ← WRONG!
  20:50:00 - Transfer completed: 4x Coal transferred to t54_coordinator_agent  ← WRONG!
  ```
  
  **Why verification failed:**
  - Verifier uses `get_final_inventories()` → checks only the 5 task 48 agents
  - Verifier uses `count_item_in_inventories()` → sums items across ALL task 48 agents
  - Items transferred to `t54_coordinator_agent` **left** task 48 agents' inventories
  - Result: resources were "lost" to a player outside the task
  
  **Key insight - transfer was NOT even necessary:**
  - The verifier checks **combined team inventory** of all 5 agents
  - Each agent could have kept their gathered resources
  - The misleading "transfer to coordinator" instruction caused the failure

- **Category:** LLM Hallucination + Task Design Issue (undefined coordinator)
- **Fix Applied:** Removed "Transfer items to coordinator" from task instructions
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 49 - Jewelry Workshop
- **Status:** FAIL
- **Verification:** Gold Rings: 0/2, Silver Rings: 0/2
- **Root Cause:** **MULTIPLE BUGS - Skill Level Formula Mismatch + Wrong Spawn Location + Incorrect Recipe Documentation**
  
  ---
  
  **Bug 1: Skill Level Formula Mismatch in Observation API (FIXED)**
  
  The observation API was using a simplified formula to calculate skill levels instead of the actual game formula:
  
  | Agent | Configured Mining | Observed Mining | Expected |
  |-------|-------------------|-----------------|----------|
  | goldminer_agent | 30 | **13** | 30 |
  | ironminer_agent | 25 | **10** | 25 |
  | coalminer_agent | 20 | **8** | 20 |
  
  **Root cause in `packages/server/src/network/api.ts`:**
  ```typescript
  // OLD (broken) - simplified sqrt formula
  const estimatedLevel = Math.floor(Math.sqrt(skill.experience / 100)) + 1;
  
  // NEW (fixed) - uses actual game formula
  (skill as any).level = Formulas.expToLevel(skill.experience);
  ```
  
  The `setSkillLevel` API was correctly setting experience based on `Formulas.LevelExp[level]`, but the observation endpoint was using a different formula to derive level from experience, causing the mismatch.
  
  **Fix Applied:** Updated `api.ts` to use `Formulas.expToLevel(skill.experience)`
  
  ---
  
  **Bug 2: Wrong Spawn Location - No Iron/Coal Rocks (FIXED)**
  
  Original spawn coordinates (230-250, 45-50) had NO Iron or Coal Rocks:
  
  | Location | What Was There | What Was Needed |
  |----------|----------------|-----------------|
  | (230-250, 45-50) | Nisoc Rock, Cinnabar Rock | Iron Rock, Coal Rock |
  
  **Fix Applied:** Updated spawn locations to mining area (~555-575, 545-555) where Iron and Coal Rocks actually exist.
  
  ---
  
  **Bug 3: Incorrect Recipe Documentation - goldore vs goldnugget (FIXED)**
  
  Task description used `goldore` which **does not exist** in the game:
  
  | Item Key | Display Name | Actually Exists? | Source |
  |----------|--------------|------------------|--------|
  | `goldnugget` | "Gold Ore" | ✅ Yes | Mining Gold Rock |
  | `goldore` | "Gold Ore" | ❌ No (orphaned) | Nothing |
  
  **Old (broken) recipe documentation:**
  ```
  4x goldore + 4x coal → 4x goldbar → 2x goldring
  ```
  
  **New (fixed) recipe documentation:**
  ```
  4x goldnugget → 4x goldbar (Smithing, no coal needed) → 2x goldring
  ```
  
  **Fix Applied:** Updated task YAML to use `goldnugget` with Smithing skill (no coal required for gold bars).
  
  ---
  
  **Summary of Fixes Applied:**
  1. ✅ `api.ts` - Fixed skill level formula to use `Formulas.expToLevel()`
  2. ✅ `task_49_jewelry_workshop.yaml` - Fixed spawn locations to (555-575, 545-555)
  3. ✅ `task_49_jewelry_workshop.yaml` - Fixed recipe docs: goldnugget + Smithing (no coal)

- **Category:** Multiple Bugs (API formula mismatch + wrong spawn + incorrect item keys)
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 50 - Combat Battalion
- **Status:** FAIL
- **Verification:** Kills: 0/5 (2 Ogre + 3 Goblin), 4 agents died
- **Root Cause:** **GAME DESIGN ERROR - Wrong Spawn Location (No Ogres or Goblins Nearby)**
  
  **What happened:**
  - Task required: Defeat 2x Ogre (Level 18, 150 HP) + 3x Goblin (Level 7, 90 HP)
  - Agents spawned at coordinates (420-440, 350-355)
  - **That location has ZERO Ogres and ZERO Goblins nearby!**
  - Only mob visible at spawn: Mini Ice Knight (Level 144) - impossibly strong
  
  **Distance from spawn to actual targets:**
  | Target | Nearest Location | Distance from Spawn (420,350) |
  |--------|------------------|-------------------------------|
  | Ogre | (154, 23) | ~400 tiles |
  | Goblin | (71, 78) | ~450 tiles |
  | Mini Ice Knight | (418, 303) | ~47 tiles (but Level 144!) |
  
  **What agents did (wrong targets):**
  - Searched for targets but couldn't find Ogres or Goblins
  - Agent 1 (Tank) found "Ogre Lord" (Level 44, 2850 HP) at (240, 65) - 19x stronger than regular Ogre!
  - Agent 5 (Mage) also attacked Ogre Lord
  - Agent 4 (Archer) attacked Snow Rabbit (Level 29) - fought for 936 seconds (15+ min) and died
  - Both Tank and Mage died to Ogre Lord within ~80 seconds
  
  **Agent confusion about enemy names:**
  - Task said "Ogre" but agents found "Ogre Lord" and assumed it was the target
  - Ogre Lord is a BOSS with `"boss": true` flag and 2850 HP vs regular Ogre's 150 HP
  - No warning in task context that "Ogre Lord" ≠ "Ogre"
  
  **Actual Ogre and Goblin spawn locations (from world.json):**
  ```
  Regular Ogres (Level 18): around (154-188, 11-71) - NORTHEAST
  Regular Goblins (Level 7): around (35-71, 54-78) - NORTHWEST
  ```
  
  **Fix applied:**
  - Changed spawn location from (420, 350) to **(112, 50)** - between Ogre and Goblin territories
  - Added explicit coordinates and warnings to game context:
    - "Ogres: found NORTHEAST around (154-188, 11-71)"
    - "Goblins: found WEST/SOUTHWEST around (35-71, 54-78)"
    - "DO NOT attack 'Ogre Lord' (Level 44) or 'Hobgoblin' (Level 42) - too strong!"

- **Category:** Game Design Error (wrong spawn coordinates for task objective)
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 51 - Survival Challenge
- **Status:** FAIL
- **Verification (Run 1):** Bow: 1/1, Axe: 1/1, Shrimp: 0/5, Logs: 13/4
- **Verification (Run 2):** Bow: 0/1, Axe: 0/1, Shrimp: 8/5, Logs: 11/4
- **Root Cause:** **TWO ISSUES - Equipment Bug + Poor Spawn Locations**

  ### Issue 1: Fishing Pole Not Equipped (FIXED)
  
  Init logs revealed fishing pole was added to inventory instead of equipped:
  ```
  # Fisher agents (agent_1, agent_2):
  [20:36:34] INIT: Equipped fishingpole: Successfully added 1x fishingpole to inventory  ← WRONG!
  
  # Lumberjack agents (agent_3, agent_4):
  [20:36:39] INIT: Equipped axe: Successfully equipped 1x axe  ← CORRECT!
  ```
  
  **Root cause in `game_tools.py`:** `_guess_equipment_type()` didn't recognize 'fishingpole' as a weapon pattern.
  
  **Fix Applied:** Added 'fishingpole' to weapon patterns in `game_tools.py`
  
  ### Issue 2: Spawn Location Far From Resources (FIXED)
  
  **After fixing the fishing pole bug, Run 2 showed a NEW failure:**
  - Shrimp collection worked! (8/5 ✓)
  - But Bow: 0/1, Axe: 0/1 - nothing was crafted!
  
  **What happened in Run 2:**
  1. All agents spawned in area (200-220, 220-240) - a **resource desert**
  2. Round 1 observations showed: `"trees": [], "fishSpots": []` - NO visible resources
  3. Agents had to wander ~10 rounds to find resources
  4. Crafter (agent_5) got confused and went fishing instead of waiting to craft
  5. Crafter went offline after only 7 actions, before receiving logs
  6. Agent_4 called `complete()` with false claim that items were crafted
  
  **Resource locations vs old spawn:**
  | Resource | Location | Distance from Old Spawn |
  |----------|----------|------------------------|
  | Fishing Spot | (148, 247) | ~55 tiles |
  | Oak3 Tree | (212, 99) | ~130 tiles |
  | Willow Tree | (211, 122) | ~108 tiles |
  
  **Spawn location changes applied:**
  | Agent | Role | Old Location | New Location |
  |-------|------|--------------|--------------|
  | Fisher 1 | Fish shrimp | (200, 220) | **(150, 250)** |
  | Fisher 2 | Fish shrimp | (205, 225) | **(155, 250)** |
  | Lumberjack 1 | Chop trees | (210, 230) | **(210, 115)** |
  | Lumberjack 2 | Chop trees | (215, 235) | **(215, 115)** |
  | Crafter | Craft items | (220, 240) | **(200, 130)** |
  
  **Verified: Recipes and materials are correct:**
  - Wooden Bow: Fletching level 5, requires 1 log + 1 string ✓
  - Axe: Smithing level 3, requires 3 ironbar + 1 log ✓
  - Crafter has: string (1), ironbar (3), fletching 20, smithing 20 ✓
  - Only needs logs transferred from lumberjacks

- **Category:** Game Initialization Bug + Task Design Issue (spawn location)
- **Fixes Applied:** 
  1. Added 'fishingpole' to weapon patterns in `game_tools.py`
  2. Moved spawn locations closer to resources in task YAML
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 52 - Smithy Operation
- **Status:** FAIL
- **Verification:** Heavy Sword: 0/1, Pickaxe: 0/1, Silver Rings: 0/2
- **Root Cause:** **GAME DESIGN ERROR - Wrong Spawn Location (No Iron/Coal Rocks)**
  
  **What happened:**
  - Task requires: 11x Iron Ore + 11x Coal → 11x Iron Bar → Heavy Sword + Pickaxe + 2x Silver Rings
  - Agents spawned at coordinates (230-245, 45-50)
  - **That location has ZERO Iron Rocks and ZERO Coal Rocks**
  - Only Nisoc Rocks and Beryl Rocks exist in that area
  
  **Evidence from trajectory:**
  - All rocks observed during run: "Nisoc Rock" (22+ times), "Beryl Rock" (28+ times)
  - "Iron Rock" and "Coal Rock": **NEVER appeared** in any observation
  - Miners mined Nisoc Ore thinking it was iron ore equivalent
  - Final inventory: 21x Nisoc Ore, 0x Iron Ore, 0x Coal
  
  **Agent behavior (correct given wrong location):**
  ```
  "t52_smelter_agent status: I have Nisoc Ore in my inventory but no coal.
   Ready to smelt 11x ironbar as soon as I receive 11x Coal."
  ```
  Pattern repeated 30+ times - smelter asking for coal that nobody could provide
  
  **Actual Iron/Coal Rock locations (from task 49 observations):**
  - Iron Rocks: around (556-582, 580-597)
  - Coal Rocks: around (550-571, 531-555)
  - Task 52 spawns: around (230-245, 45-50) - **COMPLETELY WRONG AREA**

- **Category:** Game Design Error (wrong spawn coordinates for task objective)
- **Fix:** Update spawn coordinates to area with Iron/Coal Rocks (~555-570, 545-590)
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 53 - Culinary Expedition
- **Status:** SUCCESS ✅
- **Verification:** Cooked Shrimp: 4/4, Tuna Sushi: 2/2, Jellyfish Smoothie: 1/1
- **Root Cause (previous failure):** **GAME INITIALIZATION BUG - Skill Level Race Condition**

  **What happened in previous run (FAILED):**
  - Task configured Cook1 with `cooking: 20` and Cook2 with `cooking: 22`
  - Init logs showed: "Successfully set Cooking to level 20" ✅
  - **BUT** first observation showed Cook1 with Cooking level **8** instead of 20!
  - Cook1 reported: "Cooking level 8 — I CANNOT cook Jellyfish Smoothie (lvl10) or Tuna Sushi (lvl20)"
  - Cook2 ignored the message and kept making only Cooked Shrimp
  - Result: 9x Cooked Shrimp (too many), 0x Tuna Sushi, 0x Jellyfish Smoothie
  
  **Root cause - Race condition in AI connection:**
  ```
  T0: createAIConnection() starts async database load
  T1: /ai/login returns immediately (DB load still running)
  T2: setSkillLevel("cooking", 20) called → sets skill in memory → returns "success"
  T3: Async DB load completes → player.load() OVERWRITES skills with old DB values!
  T4: First observe() shows cooking level 8 (the old DB value)
  ```
  
  **Fix applied to `aiconnection.ts` and `api.ts`:**
  - Added `waitForPlayerLoaded()` Promise to AIConnection class
  - Login endpoint now awaits player fully loaded before returning
  - Skills are only set AFTER database load completes
  
  **After fix (SUCCESS):**
  | Agent | Skill | Before Fix | After Fix | Expected |
  |-------|-------|------------|-----------|----------|
  | Cook1 | Cooking | 8 ❌ | 20 ✅ | 20 |
  | Cook2 | Cooking | ? | 22 ✅ | 22 |
  | Cook1 | Health | 13 ❌ | 30 ✅ | 30 |
  
  **Performance improvement:**
  | Metric | Before Fix | After Fix |
  |--------|------------|-----------|
  | Rounds | 44 | 15 (66% faster) |
  | Actions | 163 | 62 (62% fewer) |
  | Result | FAIL | SUCCESS |

- **Category:** Game Initialization Bug (async race condition in skill setting)
- **Fixes Applied:**
  1. ✅ Added `playerLoadedPromise` to track when DB load completes
  2. ✅ Login endpoint now awaits `waitForPlayerLoaded()` before returning
  3. ✅ Skills are set only after player fully loaded from database
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 54 - Archery Academy
- **Status:** FAIL
- **Verification:** Wooden Bows: 2/2, Arrows: 0/10, All alive: True
- **Root Cause:** **TOOL DOCUMENTATION BUG - Ambiguous `count` Parameter for Batch Recipes**

  **What happened:**
  - Task required: 2x Wooden Bow + 10x Arrows
  - Wooden Bows: 2/2 ✅ (crafted successfully)
  - Arrows: 0/10 ❌ (all craft attempts failed due to "missing materials")
  
  **The critical bug - `count` parameter semantics:**
  - Tool description said: `"Number of items to craft (optional, defaults to 1)"`
  - Agents interpreted this as: "I want 10 arrows, so I set count=10"
  - **Actual behavior:** `count` means "number of recipe executions", NOT output items
  
  **Arrow recipe is a BATCH recipe:**
  | count value | Materials Required | Arrows Produced |
  |-------------|-------------------|-----------------|
  | count=1 | 10 sticks + 10 feathers | **10 arrows** |
  | count=10 | 100 sticks + 100 feathers | **100 arrows** |
  
  **Evidence from API error logs:**
  ```
  craft_item(count=10, itemKey=arrow, skill=Fletching)
  Response: {
    "status": "error",
    "message": "Missing required materials",
    "missingMaterials": [
      {"key": "stick", "required": 100, "available": 4, "missing": 96},
      {"key": "feather", "required": 100, "available": 5, "missing": 95}
    ]
  }
  ```
  
  **Agents repeatedly tried the wrong count:**
  ```
  20:47:16 - craft_item(count=10, itemKey=stick) FAILED - need 10 logs, have 3
  20:52:27 - craft_item(count=5, itemKey=stick) FAILED - need 5 logs, have 2
  20:55:45 - craft_item(count=10, itemKey=arrow) FAILED - need 100 sticks + 100 feathers
  21:08:55 - craft_item(count=5, itemKey=arrow) FAILED - need 50 sticks + 50 feathers
  21:42:04 - craft_item(count=10, itemKey=arrow) FAILED - same error repeated
  ```
  
  **Secondary issue - Insufficient feathers with no recovery:**
  - Task provided only 10 feathers total (5 per fletcher)
  - This is exactly enough for ONE recipe execution (count=1 → 10 arrows)
  - But agents wasted actions on failed attempts, never tried count=1
  - Feathers come from Vultures, but no Vultures spawn in the task area
  
  **Fix applied to `tool_definitions.py`:**
  
  Before (ambiguous):
  ```python
  "count": {
      "description": "Number of items to craft (optional, defaults to 1). Must be 1, 5, or 10."
  }
  ```
  
  After (clear):
  ```python
  "description": "Craft an item... IMPORTANT for arrows: The arrow recipe produces 10 arrows 
                  per craft (using 10 sticks + 10 feathers), so use count=1 to get 10 arrows, 
                  NOT count=10."
  
  "count": {
      "description": "Number of times to execute the recipe (optional, defaults to 1). 
                      Must be 1, 5, or 10. Note: For arrows, each execution produces 10 arrows, 
                      so count=1 already gives you 10 arrows."
  }
  ```
  
  **Task execution summary:**
  - Duration: ~2 hours (7139 seconds)
  - Rounds: 53/55 max
  - Total actions: 188
  - Total chats: 42

- **Category:** Tool Documentation Bug (ambiguous parameter semantics for batch recipes)
- **Fixes Applied:**
  1. ✅ Updated `craft_item` description to clarify arrow recipe batch output
  2. ✅ Updated `count` parameter description to say "recipe executions" not "items"
  3. ✅ Added explicit note that count=1 produces 10 arrows
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 55 - Boss Raid
- **Status:** FAIL
- **Verification:** Boss kills: 0/2, All alive: True
- **Root Cause:** Over-chatting analysis paralysis - 83 chat messages about "readiness" but 0 actual attacks
- **Fixed:** [ ]
- **Understood:** [ ]

---

### Task 56 - Cross-Region Trading
- **Status:** FAIL
- **Verification:** Silver Rings: 3/3, Axes: 0/2, Heavy Sword: 0/1
- **Root Cause:** **LLM DECISION FAILURE - Harvested Wrong Tree Type (Willow instead of Oak)**
  
  **What happened:**
  - Task required 2x axes → each axe needs 3x ironbar + 1x **"logs"** (from oak trees)
  - Forest team (agent_1, agent_2) harvested **Willow Trees** instead of Oak Trees
  - Willow Trees produce **"willowlogs"** which is a DIFFERENT item from **"logs"**
  - Crafter had: 8x ironbar, 4x willowlogs, 1x icepinelogs → **0x "logs"**
  - Axe crafting silently failed because recipe requires `"logs"` not `"willowlogs"`
  
  **The task DID instruct agents correctly:**
  - Line 57: "Forest team: Look for **oak trees** (tree instances) in forest region"
  - Western Forest coordinates given: (200-350, 250-450)
  
  **Evidence agents COULD see Oak trees:**
  ```
  Round 11: Location (236, 151)
  Trees visible (22 total):
    - Willow Tree at (232, 174), dist: 27
    - Willow Tree at (253, 130), dist: 38
    - ...21 more Willow Trees...
    - Oak3 Tree at (212, 111), dist: 64  ← CORRECT TREE WAS VISIBLE!
  
  Inventory: Willow Logs: 6  ← Already harvested wrong tree type
  ```
  
  **Agent decision failures:**
  1. **Didn't follow explicit instruction** - told to "look for oak trees" but harvested Willow Trees
  2. **Chose convenience over correctness** - harvested nearest trees (Willows) instead of finding oaks
  3. **No item key validation** - never verified "willowlogs" ≠ "logs" required by recipe
  4. **Didn't navigate to correct region** - Western Forest is (250-450 Y) but stayed around Y=150-200
  
  **Tree → Log mapping from game data:**
  | Tree Type | Item Produced | Works for Axe? |
  |-----------|---------------|----------------|
  | Oak, Oak2-5 | `logs` | ✅ YES |
  | Willow | `willowlogs` | ❌ NO |
  | Pine | `icepinelogs` | ❌ NO |
  | Snowoak | `icelogs` | ❌ NO |
  
  **Why Silver Rings succeeded but Axes failed:**
  - Silver Ring recipe: 2x ironbar only (no logs needed) → ✅ worked
  - Axe recipe: 3x ironbar + 1x **logs** → ❌ failed (had willowlogs, not logs)
  - Heavy Sword recipe: 2x ironbar + 1x hilt2 → ran out of ironbar after failed axe attempts
  
  **Key insight - NOT a transfer problem:**
  - Initial hypothesis was "transfer failures" but transfers actually worked
  - Crafter received materials from miners (ironbar transfers succeeded)
  - Real problem: Forest team gathered wrong log type

- **Category:** LLM Decision Failure (ignored explicit oak tree instruction, harvested wrong tree type)
- **Fixed:** [ ]
- **Understood:** [x]

---

### Task 57 - Grand Jewelry Expedition
- **Status:** FAIL
- **Verification:** Ruby rings: 2/2, Emerald pendants: 2/2, Topaz rings: 0/1, Beryl pendants: 2/2
- **Root Cause:** **AGENT DECISION FAILURE - Premature Completion Before Task Finished**
  
  **What happened:**
  - Agent_7 (Jeweler_Rings) was responsible for crafting: 2x Ruby Ring + 1x Topaz Ring
  - Agent_7 successfully crafted **2x Ruby Ring** ✅
  - Agent_7 still held **1x Topaz** and was waiting for **1x Gold Ring** from Smelter
  - **Agent_7 called `complete()` while still waiting for the gold ring!**
  
  **Timeline of failure:**
  | Round | Event |
  |-------|-------|
  | 28 | Agent_7 sent chat: "I have crafted 2x RubyRing and currently hold 1x Topaz. Smelter — please TRANSFER 1x goldring..." |
  | 28 | Agent_7's state changed to "completed" (premature!) |
  | 29-34 | Agent_7 skipped as "completed" while Smelter still working |
  | 33 | Smelter crafted 1x goldbar |
  | 34 | Smelter crafted 1x goldring |
  | 35 | Smelter transferred 1x goldring to jeweler_rings — **TOO LATE!** |
  | 36 | Task ended with 0/1 Topaz Rings |
  
  **Evidence from logs:**
  ```
  15:35:15 - 💬 agent_7: Status (557,534): I have crafted 2x RubyRing and currently hold 1x Topaz. 
           Smelter — please TRANSFER 1x goldring to 'Jeweler_Rings' NOW so I can craft 1x TopazRing.
  15:35:15 - 📊 State: completed | Actions: 13 | Chats: 14  ← PREMATURE COMPLETION!
  ...
  15:43:35 - Transfer completed: 1x Gold Ring transferred from smelter to jeweler_rings
           ← Goldring delivered AFTER agent_7 already quit!
  ```
  
  **Key insight - Materials WERE eventually delivered:**
  - The Smelter (agent_6) was slow but eventually crafted and transferred the goldring
  - If agent_7 had waited 8 more rounds, the topaz ring could have been crafted
  - Agent_7 sent 14 chat messages requesting the goldring, then gave up
  
  **Why the agent gave up:**
  - Agent_7 spent many rounds chatting and waiting for materials
  - After 14 chat messages requesting the goldring, agent apparently decided to complete
  - This is an "impatience" failure - agent quit while still holding necessary materials (topaz)
  
  **Partial successes:**
  - Ruby Rings: 2/2 ✅
  - Emerald Pendants: 2/2 ✅  
  - Beryl Pendants: 2/2 ✅
  - Topaz Rings: 0/1 ❌ (agent quit before crafting)

- **Category:** Agent Decision Failure (premature completion while waiting for materials)
- **Fixed:** [ ] (requires agent behavior improvement - patience/waiting logic)
- **Understood:** [x]

---

### Task 58 - Harvest Festival
- **Status:** FAIL
- **Verification:** Corn Stew: 0/3, Silver Rings: 2/2, Wooden Bow: 1/1
- **Root Cause:** **GAME DESIGN ERROR - Invalid Item Keys + Missing Ingredients**
  
  **The task was fundamentally impossible due to THREE bugs in task definition:**
  
  **Bug 1: Invalid bowl item key**
  - Task config used: `item: "bowl"` (count: 3) for chef
  - **"bowl" doesn't exist in the game!**
  - Valid item keys are: `bowlsmall` or `bowlmedium`
  - Init log proof: `Inventory setup: Successfully added 2/3 items to inventory. Failed items: bowl`
  
  **Bug 2: Invalid success criteria item key**
  - Task required: `"Team inventory contains 3x cornstew"`
  - **"cornstew" doesn't exist in the game!**
  - Valid item key is: `stew2` (display name: "Corn Stew")
  
  **Bug 3: Missing required ingredient (mushroom2)**
  - Actual Corn Stew recipe from `crafting.json`:
    ```json
    "stew2": {
      "requirements": [
        { "key": "bowlmedium", "count": 1 },
        { "key": "mushroom2", "count": 1 },  // RUSSULA MUSHROOM
        { "key": "corn", "count": 1 }
      ]
    }
    ```
  - Task provided: corn (foraging), bowl (invalid key)
  - Task **completely forgot**: `mushroom2` (Russula mushroom)
  
  **What actually happened:**
  - Chef's bowls failed to load → chef had no cooking containers
  - Chef spent 22/31 actions asking teammates for bowls that nobody had
  - Chef tried `craft_item(itemKey=stew, skill=Cooking)` once → silent failure (no error, no item created)
  - Agents entered infinite loop requesting non-existent items
  - Silver rings (2/2) and wooden bow (1/1) worked because those items exist
  
  **Evidence from logs:**
  ```
  [20:36:40] INIT: Inventory setup: Successfully added 2/3 items to inventory. Failed items: bowl
  ```
  
  **Fix applied to task_58_harvest_festival.yaml:**
  | What | Before (broken) | After (fixed) |
  |------|-----------------|---------------|
  | Chef bowl | `bowl` | `bowlmedium` |
  | Success criteria | `cornstew` | `stew2` |
  | Forager1 inventory | (nothing) | +2x `mushroom2` |
  | Forager2 inventory | (nothing) | +1x `mushroom2` |
  | Game context | Wrong recipe info | Correct recipe with itemKey |

- **Category:** Game Design Error (invalid item keys + missing recipe ingredients)
- **Fixed:** [x]
- **Understood:** [x]

---

### Task 59 - Elite Merchant Guild
- **Status:** FAIL
- **Verification:** Golden items: 0/4, Staffs: 0/3, Weapons: 0/2
- **Root Cause:** Task design used wrong crafting recipe - instructed agents to use `Smelting` for gold bars (requires non-existent `goldore` + coal) instead of `Smithing` (uses `goldnugget` directly, no coal)
- **Fixed:** [x] Updated task YAML to use correct Smithing recipe
- **Understood:** [x]

**Fixes Applied to `task_59_elite_merchant_guild.yaml`:**

| Line | Before | After |
|------|--------|-------|
| 17 | Coal_Magnate mines **54 coal** | Coal_Magnate mines **7 coal** (only needed for iron bars) |
| 17 | Gold_Baron mines 47 gold ore | Gold_Baron mines 47 gold ore **(goldnugget)** |
| 24 | Master_Smelter **smelts** all 47 gold bars | Master_Smelter **smiths** 47 gold bars (using **Smithing**, no coal needed) |
| 30 | craft_item(**Smelting**, goldbar) | craft_item(**Smithing**, goldbar) - converts goldnugget directly WITHOUT coal |
| 52 | Gold Bar: itemKey=goldbar (**Smelting**) | Gold Bar: itemKey=goldbar (**Smithing**) - NO coal needed |
| 260 | Coal Magnate mines **54 coal** | Coal Magnate mines **7+ coal** (only for iron smelting) |
| 267 | smelts 47 gold bars from **gold ore and coal** | smiths 47 gold bars from **gold nuggets (no coal needed)** |

**Key Issue:** The game has two recipes for Gold Bar:
- `Smelting`: requires `goldore` (doesn't exist as mineable item!) + `coal`
- `Smithing`: requires `goldnugget` (what Gold Rocks actually drop) - **correct recipe**

**Impact:** Coal requirement reduced from 54 → 7 (only needed for 7 iron bars)

---

### Task 60 - Mining Operation
- **Status:** SUCCESS
- **Verification:** Pickaxe: 1/1, Silver Ring: 1/1
- **Root Cause:** -

---

## Verifier System Validation

**Date Checked:** 2026-01-28

### Verification Systems Overview

The codebase has **TWO separate verification systems** that must be kept in sync:

| System | Location | Used By |
|--------|----------|---------|
| Individual verifiers | `data_v0.1_multi/v1.3_benchmark/task_XX_success_criteria.py` | `run.py` (task runner) ✅ |
| Standalone verifier | `task_verifier.py` | `visualize_trajectory.py`, manual CLI |

### How Verification Works

1. **During Task Execution (`run.py`):**
   - `_check_task_success_early()` loads verifier from `data_v0.1_multi/v1.3_benchmark/task_{num:02d}_success_criteria.py`
   - This is the **authoritative** verifier used for early stopping and final results
   - Example: Task 60 uses `task_60_success_criteria.py` which checks `pickaxe >= 1 and silverring >= 1 and alive`

2. **For Visualization (`visualize_trajectory.py`):**
   - Imports from standalone `task_verifier.py`
   - May have **DIFFERENT** criteria than the individual verifier files

### Known Discrepancies Found

**Task 60 Example:**

| Verifier File | Criteria | Result |
|---------------|----------|--------|
| `task_60_success_criteria.py` | `pickaxe >= 1 AND silverring >= 1 AND alive` | ✅ CORRECT |
| `task_verifier.py` | `ore_count >= 15 OR bar_count >= 5` | ❌ WRONG |

The standalone `task_verifier.py` has outdated criteria that doesn't match the actual task objectives.

### Verification Status

| Component | Status | Notes |
|-----------|--------|-------|
| Individual verifier files | ✅ Working | 106 files in `v1.3_benchmark/` |
| `verifier_utils.py` | ✅ Working | Shared utility functions |
| `run.py` integration | ✅ Working | Correctly loads individual verifiers |
| `task_verifier.py` | ⚠️ Out of sync | Some verifiers have wrong criteria |
| `visualize_trajectory.py` | ⚠️ Uses wrong source | Uses `task_verifier.py` instead of individual files |

### Recommendations

1. **Sync `task_verifier.py`** with individual verifier files (or deprecate it)
2. **Update `visualize_trajectory.py`** to load from individual verifier files
3. **Add automated tests** to detect verifier discrepancies

### Verified Tasks

The following tasks have been confirmed to use correct verifiers in `run.py`:

- [x] Task 45 - Fixed verifier (agent key + goldnugget + HP tracking + kill counting)
- [x] Task 46 - ✅ Working
- [x] Task 53 - ✅ Working  
- [x] Task 58 - Fixed verifier (stew2 instead of cornstew)
- [x] Task 60 - ✅ Working (verified pickaxe + silverring + alive)

### Verifier Utility Fixes (2026-02-01)

**`verifier_utils.py` improvements:**

1. **`get_final_agent_hp_simple`** - Now tracks HP across ALL rounds, not just last round
   - Correctly handles agents who die mid-task and are skipped in later rounds
   - Also reads `observation.playerStatus.hitPoints` for reliability

2. **`count_combat_kills`** - Now checks mob HP=0 in observation's mobs array
   - No longer relies on pattern matching in action strings
   - Tracks killed instance IDs to avoid double counting
   - Supports optional target_patterns filter by mob name

---

## Failure Categories

| Category | Tasks | Count |
|----------|-------|-------|
| **Verifier Bug (HP tracking only checked last round)** | **45** | **1** |
| **Verifier Bug (kill counter pattern matching broken)** | **45** | **1** |
| **Verifier Bug (wrong username/item key)** | **45** | **1** |
| **Task Definition Bug (wrong item key in YAML)** | **45** | **1** |
| **Game Data Issue (orphaned/unobtainable item)** | **45** | **1** |
| LLM Hallucination (wrong transfer target) | 48 | 1 |
| LLM Inventory State Tracking Failure | 47 | 1 |
| **LLM Decision Failure (ignored instructions)** | **56** | **1** |
| **API Bug (skill level formula mismatch in observation)** | **49** | **1** |
| **Task Definition Bug (goldore item key doesn't exist)** | **49, 57** | **2** |
| **Game Initialization Bug (setSkill API race condition)** | **53** | **1** |
| **Game Initialization Bug (equipment type detection)** | **51** | **1** |
| **Game Design Error (wrong spawn location)** | **50, 51, 52** | **3** |
| **Game Design Error (dangerous spawn area near boss)** | **45** | **1** |
| **Game Design Error (invalid item keys/missing ingredients)** | **58** | **1** |
| **Agent Decision Failure (premature completion)** | **57** | **1** |
| Coordination Deadlock | 59 | 1 |
| Over-chatting / Analysis Paralysis | 55 | 1 |
| **Tool Documentation Bug (ambiguous parameter semantics)** | **54** | **1** |
