# Kaetram Crafting System Documentation

This document explains the crafting system in Kaetram, including how crafting recipes are defined, skills involved, and how AI agents can interact with the crafting system.

## Crafting Skills

Kaetram features several crafting skills, each with its own set of recipes:

| Skill | Description | Primary Materials |
|-------|-------------|-------------------|
| Smithing | Create weapons, armor, and tools using metal bars | Metal bars (Bronze, Iron, Gold, etc.) |
| Cooking | Prepare food that restores health/status | Raw food items |
| Crafting | Create various utility items and accessories | Multiple resources (gems, strings, etc.) |
| Fletching | Create bows, arrows, and ranged equipment | Wood, feathers, metal tips |
| Alchemy | Create potions and magical items | Herbs, reagents |
| Smelting | Convert ores into metal bars | Ores (various types) |
| Chiseling | Create decorative items from stone | Stone materials |

## Recipe Structure

All crafting recipes in Kaetram follow a common JSON structure:

```json
{
  "itemKey": {
    "level": 10,             // Required skill level
    "experience": 35,        // Experience awarded for crafting
    "requirements": [        // Materials required for crafting
      {
        "key": "material1",  // Item key for required material
        "count": 3           // Number of this material needed
      },
      {
        "key": "material2",
        "count": 1
      }
    ],
    "result": {
      "count": 1             // Number of items produced
    }
  }
}
```

## Example Recipes

### Smithing Example: Bronze Axe
```json
{
  "bronzeaxe": {
    "level": 1,
    "experience": 35,
    "requirements": [
      {
        "key": "bronzebar",
        "count": 3
      },
      {
        "key": "logs",
        "count": 1
      }
    ],
    "result": {
      "count": 1
    }
  }
}
```

### Cooking Example: Stew
```json
{
  "stew": {
    "level": 1,
    "experience": 50,
    "requirements": [
      {
        "key": "bowlmedium",
        "count": 1
      },
      {
        "key": "mushroom1",
        "count": 1
      },
      {
        "key": "tomato",
        "count": 1
      }
    ],
    "result": {
      "count": 1
    }
  }
}
```

### Crafting Example: Ruby Pendant
```json
{
  "rubypendant": {
    "level": 20,
    "experience": 145,
    "requirements": [
      {
        "key": "ruby",
        "count": 1
      },
      {
        "key": "string",
        "count": 1
      }
    ],
    "result": {
      "count": 1
    }
  }
}
```

## Crafting Workflow

1. **Skill Level**: Each recipe requires a minimum skill level to craft.
2. **Materials Collection**: Players must gather all required materials.
3. **Crafting Interface**: The player must access the appropriate crafting interface.
4. **Material Consumption**: When crafting, the required materials are automatically removed from the player's inventory.
5. **Experience Gain**: The player receives the specified experience points in the relevant skill.
6. **Result**: The crafted item(s) are added to the player's inventory.

## Multiplier System

When crafting multiple items at once (5 or 10):
- Material requirements are multiplied by the count (e.g., crafting 5 bronze axes requires 15 bronze bars and 5 logs)
- Experience gained is also multiplied by the count

## AI Agent Crafting API

AI agents can interact with the crafting system through the `/ai/craft` endpoint:

### Request
```json
{
  "token": "YOUR_TOKEN",
  "type": "Smithing",
  "itemKey": "bronzeaxe",
  "count": 1
}
```

### Parameters
- `token`: Your AI agent's authentication token
- `type`: The crafting skill type (e.g., "Smithing", "Cooking")
- `itemKey`: The key of the item to craft
- `count`: The number of items to craft (must be 1, 5, or 10)

### Example Success Response
```json
{
  "status": "success",
  "message": "Crafted 1x bronzeaxe using Smithing skill",
  "details": {
    "skill": "Smithing",
    "itemKey": "bronzeaxe",
    "count": 1
  }
}
```

### Example Error Response: Missing Materials
```json
{
  "status": "error",
  "message": "Missing required materials",
  "missingMaterials": [
    {
      "key": "bronzebar",
      "name": "Bronze Bar",
      "required": 3,
      "available": 0,
      "missing": 3
    },
    {
      "key": "logs",
      "name": "Logs",
      "required": 1,
      "available": 0,
      "missing": 1
    }
  ],
  "requirements": [
    {
      "key": "bronzebar",
      "name": "Bronze Bar",
      "count": 3
    },
    {
      "key": "logs",
      "name": "Logs",
      "count": 1
    }
  ]
}
```

### Example Error Response: Insufficient Level
```json
{
  "status": "error",
  "message": "You need level 10 Smithing to craft this item",
  "requiredLevel": 10,
  "currentLevel": 1
}
```

## Quest Requirements

Some crafting skills require completing specific quests before they can be used:
- **Crafting**: Requires starting the crafting quest
- **Alchemy**: Requires starting the alchemy quest

## Cooldown System

There is a cooldown period between crafting operations to prevent spamming the crafting system. AI agents will receive an error message if they attempt to craft before the cooldown expires:

```json
{
  "status": "error",
  "message": "Crafting is on cooldown"
}
```

## Data Files

The crafting recipes are stored in JSON files in the server's data directory:
- `packages/server/data/crafting/alchemy.json`
- `packages/server/data/crafting/chiseling.json`
- `packages/server/data/crafting/cooking.json`
- `packages/server/data/crafting/crafting.json`
- `packages/server/data/crafting/fletching.json`
- `packages/server/data/crafting/smelting.json`
- `packages/server/data/crafting/smithing.json` 