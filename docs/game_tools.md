## Game Tools (AI Function Calling)

Below are the function-calling tools exposed to the AI agent, sourced from `agents/tool_definitions.py`. Each tool includes a description, parameters, required fields, and a minimal example arguments payload.

### Quick reference
- **move_character**: Move to coordinates `(x, y)`
- **send_chat_message**: Send a chat message (global/local)
- **enter_portal**: Enter a nearby portal/warp point
- **stop_action**: Halt movement or combat
- **equip_item**: Equip an inventory item by slot index
- **harvest_resource**: Harvest a resource using appropriate skill (chopping trees, mining rocks, fishing, foraging)
- **pickup_resource**: Pick up dropped items from the ground
- **attack_entity**: Attack a visible entity by instance ID; auto-moves and loots
- **sleep**: Wait for N seconds (cooldowns/timing)
- **craft_item**: Craft an item via a named skill
- **complete**: Finish the current task with a final response
- **chat**: Send a global group chat message to all agents/players
- **transfer_items**: Transfer items from your inventory to another player

---

### move_character
- **Description**: Move the character to specific map coordinates. Limited to maximum 32 tiles per movement.
- **Parameters**:
  - **x** (integer): X coordinate (must be within 32 tiles of current position)
  - **y** (integer): Y coordinate (must be within 32 tiles of current position)
- **Required**: `x`, `y`
- **Distance Limitation**: Maximum 32 tiles per tool call to prevent unrealistic teleportation
- **Example**:
```json
{ "x": 120, "y": 340 }
```

### send_chat_message
- **Description**: Send a chat message (local by default, or global).
- **Parameters**:
  - **message** (string): Content to send
  - **global** (boolean, optional): `true` for global, `false` for local (default `false`)
- **Required**: `message`
- **Example**:
```json
{ "message": "Hello there!", "global": true }
```

### enter_portal
- **Description**: Enter a portal/warp point near the player.
- **Preconditions**: Only when a portal is visible in the current environment observation and the player is standing close to it.
- **Parameters**: none
- **Required**: none
- **Example**:
```json
{}
```

### stop_action
- **Description**: Stop current movement or combat actions.
- **Parameters**: none
- **Required**: none
- **Example**:
```json
{}
```

### equip_item
- **Description**: Equip an item from the inventory by slot index.
- **Parameters**:
  - **index** (integer): Inventory slot index (0-based). Must match an index from the latest environment observation `inventory`.
- **Required**: `index`
- **Example**:
```json
{ "index": 5 }
```

### harvest_resource
- **Description**: Instantly harvest a resource using the appropriate skill (lumberjacking for trees, mining for rocks, fishing for fish spots, foraging for plants). Automatically moves closer if needed, completes the entire harvesting process, and collects all dropped items into inventory immediately. This is an enhanced "cheat mode" function that eliminates waiting time for AI agents.
- **Behavior**: Completes the full harvesting cycle in one call - depletes the resource and adds items to inventory instantly.
- **Preconditions**: Resource must be visible in the current environment observation under trees, rocks, fishSpots, or foraging arrays.
- **Parameters**:
  - **targetInstance** (string): Exact instance ID from the observation (e.g., `"10-12345"`).
- **Required**: `targetInstance`
- **Example**:
```json
{ "targetInstance": "10-12345" }
```

### pickup_resource
- **Description**: Pick up a dropped item or resource from the ground.
- **Preconditions**: Item must be visible and reachable in the current environment.
- **Parameters**:
  - **targetInstance** (string): Exact instance ID of the dropped item.
- **Required**: `targetInstance`
- **Example**:
```json
{ "targetInstance": "item-67890" }
```

### attack_entity
- **Description**: Attack an entity by instance ID. Automatically moves to an adjacent tile if needed, waits briefly for sync, starts combat, then moves to the target tile to auto-loot.
- **Preconditions**: Target entity must be visible in the current environment observation.
- **Parameters**:
  - **targetInstance** (string): Exact instance ID from observation (e.g., `"3995661692"`).
- **Required**: `targetInstance`
- **Example**:
```json
{ "targetInstance": "3995661692" }
```

### sleep
- **Description**: Wait for a specified number of seconds (use sparingly for timing/cooldowns).
- **Parameters**:
  - **seconds** (integer): Range 1–60
- **Required**: `seconds`
- **Example**:
```json
{ "seconds": 2 }
```

### craft_item
- **Description**: Craft an item using a specific crafting skill. Requires materials and level requirements.
- **Parameters**:
  - **skill** (string): One of `Crafting`, `Smithing`, `Fletching`, `Cooking`, `Smelting`
  - **itemKey** (string): Item key/identifier (e.g., `"staff"`, `"lightningstaff"`, `"arrow"`, `"sword2"`, `"axe"`, `"pickaxe"`)
  - **count** (integer, optional): One of `1`, `5`, `10` (default `1`)
- **Required**: `skill`, `itemKey`
- **Example**:
```json
{ "skill": "Smithing", "itemKey": "sword2", "count": 5 }
```

### complete
- **Description**: Finish the current task with a final response. Does not end the overall session.
- **Parameters**:
  - **response** (string): Summary or final message
- **Required**: `response`
- **Example**:
```json
{ "response": "Reached the town, crafted a sword, and equipped gear." }
```

### chat
- **Description**: Send a global group chat message to all agents and players in the game. This is specifically designed for multi-agent communication and coordination, and is different from `send_chat_message` as it always sends messages globally.
- **Use Cases**: Coordinating between AI agents, announcing intentions, sharing information across the game world
- **Parameters**:
  - **message** (string): The message content to broadcast to all players and agents
- **Required**: `message`
- **Example**:
```json
{ "message": "Hello fellow agents! Looking for someone to trade iron bars with." }
```

### transfer_items
- **Description**: Transfer items from your inventory to another player. This tool coordinates item transfers by notifying the target player via global chat and providing location information for meetup.
- **Behavior**: 
  - Checks if you have sufficient items in inventory
  - Sends coordination messages to the target player via global chat
  - Provides your current location for meetup
  - Requires manual coordination between players to complete the transfer
- **Parameters**:
  - **targetPlayer** (string): Exact username of the target player
  - **itemKey** (string): Key/identifier of the item to transfer (e.g., "ironbar", "sword", "healingpotion")  
  - **count** (integer): Number of items to transfer (must be positive and available in inventory)
- **Required**: `targetPlayer`, `itemKey`, `count`
- **Example**:
```json
{ "targetPlayer": "smith_test", "itemKey": "ironbar", "count": 5 }
```

---

Notes
- These tools are the officially exposed function-calling surface for the AI agent. Internal helpers like `observe_environment`, `teleport_character`, and `logout_character` exist in `agents/game_tools.py` but are not directly callable by the AI as tools.
- The following tools are intentionally not exposed to the agent: `create_character`, `login_character`, `set_combat_level`.
- Always prefer action tools (move, attack, chat, etc.) and reserve `sleep` for timing needs. Use `complete` to close out a task when done.
- **New Multi-Agent Tools**: Use `chat` for global communication and `transfer_items` for coordinating item exchanges between agents.
