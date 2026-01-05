"""
Tool definitions for Qwen Function Calling
Following the format specified in Alibaba Cloud Qwen documentation
"""

GAME_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "move_character",
            "description": "Move the character to specific coordinates on the game map. Useful for exploration and navigation across any distance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "The X coordinate to move to. Must be within 32 tiles of current position."
                    },
                    "y": {
                        "type": "integer", 
                        "description": "The Y coordinate to move to. Must be within 32 tiles of current position."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "send_chat_message",
            "description": "Send a chat message in the game. Can be used for communication with other players or NPCs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message content to send in chat."
                    },
                    "global": {
                        "type": "boolean",
                        "description": "Whether to send as global message (true) or local message (false). Default is false."
                    }
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enter_portal",
            "description": "Enter a portal or warp point when standing on it. IMPORTANT: You can only use this function if you can see a portal in your current environment observation and you are standing close to it. Check your environment observation for portals before using this function.",
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
            "name": "stop_action",
            "description": "Stop current movement or combat actions. Use this to halt ongoing activities when needed.",
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
            "name": "pickup_resource",
            "description": "Pick up a dropped item or resource from the ground. You can ONLY use this function if you can see the dropped item in your current environment observation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the dropped item to pick up. This MUST be an exact instance ID from your current environment observation."
                    }
                },
                "required": ["targetInstance"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pickup_ground_item",
            "description": "Pick up a dropped item from the ground (loot from killed mobs, etc.). These items are visible in the 'groundItems' array of your environment observation. Use this to collect loot after combat or to pick up items you find on the ground. You must be within 2 tiles of the item to pick it up.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the ground item to pick up. This MUST be an exact instance ID from the 'groundItems' section in your current environment observation (e.g., '1234567890'). Instance IDs are pure numbers without any prefix."
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
            "description": "Attack an entity directly by providing its instance ID. This function will automatically handle positioning, combat, and loot collection - it will move you close to the target if needed, initiate the attack, and after combat automatically move to the target's location to pick up any dropped items. You can ONLY use this function if you can see the target entity (monster, mob, or player) in your current environment observation.",
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
            "description": "Craft an item using the specified crafting skill. You must have the required materials in your inventory and meet the level requirements. Available crafting skills: Crafting, Smithing, Fletching, Cooking, Smelting. Common items you can craft include: staff (magic staff), lightningstaff, firestaff, icestaff, naturestaff, arrow, sword2, axe, pickaxe, etc.",
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
                        "description": "Number of items to craft (optional, defaults to 1). Must be 1, 5, or 10.",
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
            "description": "Finish your current task with a final response. Use this when you have accomplished what was asked, need to provide a summary, or when the conversation feels naturally concluded. This does not end the entire session - just the current task.",
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
            "description": "Send a global group chat message to all agents and players in the game. This is different from send_chat_message as it is specifically designed for multi-agent communication and always sends messages globally for coordination between AI agents.",
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
            "description": "Transfer items from your inventory to another player. This tool coordinates with the target player via chat messages to arrange the item transfer. The target player will be notified of the transfer request and your location.",
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
    },
    {
        "type": "function", 
        "function": {
            "name": "check_inventory_status",
            "description": "Check current inventory status without any requirements. Use this before making any claims about what items you have. Always use this tool first when discussing your inventory contents.",
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
            "name": "verify_inventory",
            "description": "Verify that specific items are in your inventory before proceeding with crafting or other actions. This helps prevent claiming to have materials you don't actually possess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "required_items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of item keys that must be present in inventory (e.g., ['logs', 'string'])"
                    }
                },
                "required": ["required_items"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discard_item",
            "description": "Discard (drop) an item from your inventory to your current location on the ground. The item will be dropped at your current position and can be picked up by you or other players later. Use this when your inventory is full and you need to make space for important items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "inventoryIndex": {
                        "type": "integer",
                        "description": "The 0-based index of the inventory slot containing the item to discard. Check your inventory status first to find the correct index."
                    },
                    "count": {
                        "type": "integer",
                        "description": "Optional: Number of items to discard if it's a stack. If not specified, all items in that slot will be discarded."
                    }
                },
                "required": ["inventoryIndex"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "destroy_item",
            "description": "Permanently destroy an item from your inventory. The item will be completely deleted and cannot be recovered. This is useful for removing unwanted items when you need inventory space and don't want to leave items on the ground. WARNING: This action cannot be undone!",
            "parameters": {
                "type": "object",
                "properties": {
                    "inventoryIndex": {
                        "type": "integer",
                        "description": "The 0-based index of the inventory slot containing the item to destroy. Check your inventory status first to find the correct index."
                    },
                    "count": {
                        "type": "integer",
                        "description": "Optional: Number of items to destroy if it's a stack. If not specified, all items in that slot will be destroyed."
                    }
                },
                "required": ["inventoryIndex"]
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