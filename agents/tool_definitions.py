"""
Tool definitions for Qwen Function Calling
Following the format specified in Alibaba Cloud Qwen documentation
"""

GAME_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "move_character",
            "description": "Move the character to specific coordinates on the game map. Maximum movement distance is 120 tiles (Manhattan distance) per move. For longer distances, use multiple moves.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "The X coordinate to move to. Must be within 120 tiles (Manhattan distance) of current position."
                    },
                    "y": {
                        "type": "integer",
                        "description": "The Y coordinate to move to. Must be within 120 tiles (Manhattan distance) of current position."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enter_portal",
            "description": "Enter a portal or warp point when standing on it. IMPORTANT: You can only use this function if you can see a portal in your current environment observation and you are standing close to it.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "equip_item",
            "description": "Equip an item from the character's inventory. IMPORTANT: You can only use this function if you can see items in your inventory from your environment observation. Check the 'inventory' section in your environment observation to see available items and their slot indices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "The inventory slot index of the item to equip (0-based indexing). This MUST be a valid index from the 'inventory' section in your environment observation."
                    }
                },
                "required": ["index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "harvest_resource",
            "description": "Instantly harvest a resource using the appropriate skill (lumberjacking for trees, mining for rocks, fishing for fish spots, foraging for plants). This function automatically moves closer if needed, completes the entire harvesting process, and collects all dropped items into inventory immediately in one operation. This is an enhanced mode that eliminates waiting time for AI agents. You can ONLY use this function if you can see the target resource in your current environment observation under trees, rocks, fishSpots, or foraging arrays.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the resource to harvest. This MUST be an exact instance ID from the 'trees', 'rocks', 'fishSpots', or 'foraging' sections in your current environment observation (e.g., '61889701'). Instance IDs are pure numbers without any prefix. Do not use made-up or guessed IDs."
                    }
                },
                "required": ["targetInstance"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "attack_entity",
            "description": "Attack an entity directly by providing its instance ID. This function will automatically handle positioning, combat, and loot collection - it will move you close to the target if needed, initiate the attack, and after combat automatically move to the target's location to pick up any dropped items. You can ONLY use this function if you can see the target entity (monster, mob) in your current environment observation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the entity to attack. This MUST be an exact instance ID from the 'entities' or 'mobs' section in your current environment observation (e.g., '3995661692'). Instance IDs are pure numbers without any prefix. Do not use made-up or guessed IDs. Make sure you are close to the target before attacking."
                    }
                },
                "required": ["targetInstance"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sleep",
            "description": "Wait for a specified number of seconds. Use this when you need to wait for game events, cooldowns, or IMPORTANTLY, after moving before attacking to ensure position sync with the server. Essential for successful combat timing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "integer",
                        "description": "The number of seconds to wait (minimum 1, maximum 60)."
                    }
                },
                "required": ["seconds"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "craft_item",
            "description": "Craft an item using the specified crafting skill. You must have the required materials in your inventory and meet the level requirements. Available crafting skills: Crafting, Smithing, Fletching, Cooking, Smelting. Common items you can craft include: staff (magic staff), lightningstaff, firestaff, icestaff, naturestaff, arrow, sword2, axe, pickaxe, etc. IMPORTANT for arrows: The arrow recipe produces 10 arrows per craft (using 10 sticks + 10 feathers), so use count=1 to get 10 arrows, NOT count=10.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "The crafting skill to use. Must be one of: Crafting, Smithing, Fletching, Cooking, Smelting",
                        "enum": ["Crafting", "Smithing", "Fletching", "Cooking", "Smelting"]
                    },
                    "itemKey": {
                        "type": "string",
                        "description": "The key/identifier of the item to craft (e.g., 'staff', 'lightningstaff', 'arrow', 'sword2', 'axe', 'pickaxe')"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of times to execute the recipe (optional, defaults to 1). Must be 1, 5, or 10. Note: For arrows, each execution produces 10 arrows, so count=1 already gives you 10 arrows.",
                        "enum": [1, 5, 10]
                    }
                },
                "required": ["skill", "itemKey"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete",
            "description": "Finish your current task with a final response. Use this when you believe that you have accomplished the task and you are no longer needed to help the team. Aftger triggering this function, you will be offline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "string",
                        "description": "A meaningful response describing what you accomplished or your final thoughts on the task."
                    }
                },
                "required": ["response"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": "Send a global group chat message to all agents and players in the game.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message content to send in the global group chat. This will be visible to all players and agents currently online."
                    }
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_items",
            "description": "Transfer items from your inventory to another player. This tool is capable to transfer specifitic items to another player regardless of the distance between the players. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetPlayer": {
                        "type": "string",
                        "description": "The username of the player to transfer items to. This must be an exact username of an online player."
                    },
                    "itemKey": {
                        "type": "string",
                        "description": "The key/identifier of the item to transfer from your inventory (e.g., 'ironbar', 'sword', 'healingpotion')."
                    },
                    "count": {
                        "type": "integer",
                        "description": "The number of items to transfer. Must be a positive integer and you must have at least this many items in your inventory."
                    }
                },
                "required": ["targetPlayer", "itemKey", "count"]
            }
        }
    }
]

def get_tool_definitions():
    """Return the list of tool definitions for Qwen Function Calling"""
    return GAME_TOOLS

def get_tools_as_string():
    """Return tools formatted as string for system prompt"""
    import json
    return json.dumps(GAME_TOOLS, indent=2)
