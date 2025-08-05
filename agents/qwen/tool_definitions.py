"""
Tool definitions for Qwen Function Calling
Following the format specified in Alibaba Cloud Qwen documentation
"""

GAME_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_character",
            "description": "Create a new AI character in the Kaetram game. Use this when you need to create a character for the first time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The username for the new character. If not provided, will use default 'QwenAgent'."
                    },
                    "password": {
                        "type": "string", 
                        "description": "The password for the new character. If not provided, will use default password."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "login_character",
            "description": "Login with an existing character in the Kaetram game. Use this to start a game session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The username of the existing character."
                    },
                    "password": {
                        "type": "string",
                        "description": "The password of the existing character."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_character",
            "description": "Move the character to specific coordinates on the game map. Useful for exploration and navigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "The X coordinate to move to."
                    },
                    "y": {
                        "type": "integer", 
                        "description": "The Y coordinate to move to."
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
            "name": "observe_environment",
            "description": "Observe the surrounding environment to get information about nearby entities, players, items, and terrain. Essential for situational awareness.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "radius": {
                        "type": "integer",
                        "description": "The observation radius in game units. Default is 64. Larger values give wider view but may include more data."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enter_portal",
            "description": "Enter a portal or warp point when standing on it. Used for fast travel between different areas of the game.",
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
            "description": "Equip an item from the character's inventory. Use this to improve character stats or abilities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "The inventory slot index of the item to equip (0-based indexing)."
                    }
                },
                "required": ["index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "collect_resource",
            "description": "Collect a resource using the appropriate skill (lumberjacking, mining, fishing, foraging). Use this to gather materials.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the resource to collect (e.g., tree, rock, fishing spot)."
                    }
                },
                "required": ["targetInstance"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "target_entity",
            "description": "Target an entity for interaction or combat. Use this before attacking enemies or interacting with NPCs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the entity to target (player, NPC, monster, etc.)."
                    }
                },
                "required": ["targetInstance"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "attack_target",
            "description": "Attack a targeted entity directly. Provide the target instance ID to initiate combat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "targetInstance": {
                        "type": "string",
                        "description": "The instance ID of the entity to attack (monster, player, etc.)."
                    }
                },
                "required": ["targetInstance"]
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