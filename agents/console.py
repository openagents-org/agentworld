#!/usr/bin/env python3
"""
Natural Language Game Console for Multi-LLM Agent
Interactive CLI that allows players to control the game agent using natural language.
Supports multiple LLM providers: Qwen, OpenAI, Anthropic Claude, and DeepSeek.

Usage:
    python console.py                                              # Interactive mode with default provider
    python console.py --provider openai --api-key sk-...          # Use OpenAI GPT-4
    python console.py --provider claude --api-key sk-...          # Use Anthropic Claude  
    python console.py --provider deepseek --api-key sk-...        # Use DeepSeek
    python console.py --host http://localhost:7031                 # Connect to different game server
    python console.py --task "Fight mobs until level 2"           # Single task mode
    python console.py --username myagent --password 123           # Custom credentials
    python console.py --task "Fight mobs until level 2"           # Single task mode
    python console.py --task "explore" --output game.log          # Single task with log output
    python console.py --username myagent --password 123           # Custom credentials
    python console.py --output session.log                        # Interactive mode with log file

Features:
- Multi-LLM provider support (Qwen, OpenAI, Claude, DeepSeek)
- Auto-login without prompting the LLM
- Direct natural language commands (e.g., "explore the area", "collect resources")
- Fancy console interface with emojis
- Session statistics and conversation history
- Automatic tool call execution until task completion
- Environment variable and command-line API key support

The agent handles multi-round tool calls internally and stops when no more tools are needed.
"""

import argparse
import json
import time
import sys
from typing import List, Dict, Any, Optional
from agent_factory import AgentFactory
from base_agent import BaseAgent
from config import (
    AGENT_USERNAME, 
    AGENT_PASSWORD, 
    MASTER_PASSWORD,
    DEFAULT_LLM_PROVIDER,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    DEEPSEEK_API_KEY
)


class GameConsole:
    def __init__(
        self, 
        username: str = None, 
        password: str = None, 
        provider: str = None, 
        api_key: str = None, 
        model: str = None,
        host: str = None,
        output_file: str = None,
        initial_location: tuple = None,
        combat_levels: dict = None,
        equipped_items: list = None,
        inventory_items: list = None,
        new_character: bool = False,
        dump_prompts: bool = False
    ):
        # Pass credentials to agent so it can use them for login prompts
        self.username = username or AGENT_USERNAME
        self.password = password or AGENT_PASSWORD
        self.provider = provider or DEFAULT_LLM_PROVIDER
        self.api_key = api_key
        self.model = model
        self.host = host
        self.output_file = output_file
        self.dump_prompts = dump_prompts
        
        # Initial state configuration
        self.initial_location = initial_location
        self.combat_levels = combat_levels or {}
        self.equipped_items = equipped_items or []
        self.inventory_items = inventory_items or []
        self.new_character = new_character
        
        # Create the appropriate agent using the factory
        try:
            self.agent = AgentFactory.create_agent(
                provider=self.provider,
                api_key=self.api_key,
                model=self.model,
                username=self.username,
                password=self.password,
                base_url=self.host,
                dump_prompts=self.dump_prompts
            )
        except ValueError as e:
            print(f"❌ Failed to create agent: {e}")
            sys.exit(1)
        
        self.max_iterations = 50  # Safety limit to prevent infinite loops
        self.session_logs = []
        
        # Open output file if specified
        self.log_file_handle = None
        if self.output_file:
            try:
                self.log_file_handle = open(self.output_file, 'w', encoding='utf-8')
                print(f"📝 Logging to file: {self.output_file}")
            except Exception as e:
                print(f"❌ Failed to open output file {self.output_file}: {e}")
                sys.exit(1)
        
    def log_message(self, message_type: str, content: str, metadata: Optional[Dict] = None):
        """Log a message with timestamp and formatting"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "type": message_type,
            "content": content,
            "metadata": metadata or {}
        }
        self.session_logs.append(log_entry)
        
        # Format log message for both console and file
        log_message_text = f"[{timestamp}] {message_type}: {content}"
        if metadata:
            log_message_text += f"\n    └─ {json.dumps(metadata, indent=6)}"
        
        # Write to file if output file is specified
        if self.log_file_handle:
            self.log_file_handle.write(log_message_text + "\n")
            self.log_file_handle.flush()  # Ensure immediate write
        
        # Color coding for console output
        colors = {
            "USER": "\033[94m",      # Blue
            "ASSISTANT": "\033[92m", # Green  
            "TOOL": "\033[93m",      # Yellow
            "SYSTEM": "\033[91m",    # Red
            "INFO": "\033[96m",      # Cyan
            "CHEAT": "\033[95m"      # Magenta
        }
        reset_color = "\033[0m"
        
        color = colors.get(message_type, "")
        print(f"{color}[{timestamp}] {message_type}: {content}{reset_color}")
        
        if metadata:
            print(f"    └─ {json.dumps(metadata, indent=6)}")
    
    def close_log_file(self):
        """Close the log file handle if open"""
        if self.log_file_handle:
            self.log_file_handle.close()
            self.log_file_handle = None
    

    
    def get_player_status(self) -> str:
        """Get and format player status information"""
        try:
            # Call observe_environment to get player stats (silently, without LLM)
            result = self.agent.game_tools.observe_environment({"radius": 1})
            
            if isinstance(result, str) and "Environment observation" in result:
                # Try to extract JSON from the result string
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    import json
                    data = json.loads(json_match.group())
                    player_status = data.get("playerStatus", {})
                    location = data.get("location", {})
                    
                    if player_status:  # Only proceed if we have player data
                        # Extract key stats with defaults
                        level = player_status.get("level", 1)
                        exp = player_status.get("experience", 0)
                        hp = player_status.get("hitPoints", "?")
                        max_hp = player_status.get("maxHitPoints", "?")
                        mp = player_status.get("mana", "?")
                        max_mp = player_status.get("maxMana", "?")
                        x = location.get("x", "?")
                        y = location.get("y", "?")
                        
                        # Add combat status indicator
                        combat_status = "⚔️" if player_status.get("combat", False) else ""
                        
                        # Format status line with colors for different stat types
                        return f"📊 Lv.{level} | XP:{exp} | ❤️{hp}/{max_hp} | 💙{mp}/{max_mp} | 📍({x},{y}) {combat_status}".strip()
                    
            return "📊 Status: Player data not available (no playerStatus field)"
            
        except json.JSONDecodeError as e:
            return f"📊 Status: JSON parse error ({str(e)[:20]}...)"
        except Exception as e:
            return f"📊 Status: Error ({str(e)[:30]}...)"

    def handle_teleport_command(self, command: str):
        """Handle /teleport cheat command"""
        try:
            # Parse command: /teleport x y [withAnimation] or /teleport preset
            parts = command.strip().split()
            if len(parts) < 2:
                print("❌ Invalid teleport command. Usage:")
                print("   /teleport x y [withAnimation]  - Teleport to coordinates")
                print("   /teleport spawn                - Teleport to spawn (250, 180)")
                print("   Example: /teleport 250 180")
                print("   Example: /teleport 250 180 true")
                print("   Example: /teleport spawn")
                return
            
            # Handle preset locations
            if len(parts) == 2 and parts[1].lower() == 'spawn':
                x, y, with_animation = 250, 180, False
            elif len(parts) >= 3:
                x = int(parts[1])
                y = int(parts[2])
                with_animation = parts[3].lower() == 'true' if len(parts) > 3 else False
            else:
                print("❌ Invalid teleport command. Use /teleport x y or /teleport spawn")
                return
            
            print(f"⚡ CHEAT: Teleporting bot to ({x}, {y}){' with animation' if with_animation else ''}...")
            
            # Direct teleport call without going through LLM
            result = self.agent.game_tools.teleport_character({
                "x": x,
                "y": y,
                "withAnimation": with_animation
            })
            
            print(f"✅ Teleport result: {result}")
            self.log_message("CHEAT", f"Teleported to ({x}, {y}): {result}")
            
        except ValueError:
            print("❌ Invalid coordinates. Please use integers.")
            print("   Example: /teleport 250 180")
        except Exception as e:
            print(f"❌ Teleport failed: {str(e)}")
            self.log_message("CHEAT", f"Teleport failed: {str(e)}")

    def handle_equip_command(self, command: str):
        """Handle /equip cheat command"""
        try:
            # Parse command: /equip <item_key> [count] [enchantment_level]
            parts = command.strip().split()
            if len(parts) < 2:
                print("❌ Invalid equip command. Usage:")
                print("   /equip <item_key> [count] [enchantment_level]")
                print("   Examples:")
                print("   /equip coppersword             - Give and equip copper sword")
                print("   /equip copperhelmet 1 3        - Give copper helmet with +3 enchantment")
                print("   /equip leatherarmour           - Give and equip leather armor")
                print("   /equip magicstaff              - Give and equip magic staff")
                print("")
                print("   Common item keys: coppersword, ironsword, goldensword, leatherarmour,")
                print("                     copperhelmet, ironhelmet, leathershield, coppershield")
                return
            
            item_key = parts[1].lower()
            count = int(parts[2]) if len(parts) > 2 else 1
            enchantment_level = int(parts[3]) if len(parts) > 3 else 0
            
            print(f"⚡ CHEAT: Giving and equipping {item_key} (count: {count}, enchant: +{enchantment_level})...")
            
            # Direct call to give and equip item (hypothetical admin endpoint)
            result = self.agent.game_tools.give_and_equip_item({
                "itemKey": item_key,
                "count": count,
                "enchantmentLevel": enchantment_level
            })
            
            print(f"✅ Equip result: {result}")
            self.log_message("CHEAT", f"Equipped {item_key} (x{count}, +{enchantment_level}): {result}")
            
        except ValueError:
            print("❌ Invalid numbers. Count and enchantment level must be integers.")
            print("   Example: /equip coppersword 1 3")
        except Exception as e:
            print(f"❌ Equip failed: {str(e)}")
            self.log_message("CHEAT", f"Equip failed: {str(e)}")

    def handle_setlevel_command(self, command: str):
        """Handle /setlevel cheat command"""
        try:
            # Parse command: /setlevel <level>
            parts = command.strip().split()
            if len(parts) < 2:
                print("❌ Invalid setlevel command. Usage:")
                print("   /setlevel <level>")
                print("   Examples:")
                print("   /setlevel 10     - Set all combat skills to level 10")
                print("   /setlevel 45     - Set all combat skills to level 45")
                print("   /setlevel 120    - Set all combat skills to level 120 (max)")
                print("   Note: Sets each combat skill (Accuracy, Strength, Defense, Health, Magic, Archery) to the specified level")
                return
            
            level = int(parts[1])
            if level < 1 or level > 120:
                print("❌ Level must be between 1 and 120")
                return
            
            print(f"⚡ CHEAT: Setting player level to {level}...")
            
            # Direct call to set player level (hypothetical admin endpoint)
            result = self.agent.game_tools.set_player_level({
                "level": level
            })
            
            print(f"✅ Set level result: {result}")
            self.log_message("CHEAT", f"Set level to {level}: {result}")
            
        except ValueError:
            print("❌ Invalid level. Please use an integer between 1 and 120.")
            print("   Example: /setlevel 25")
        except Exception as e:
            print(f"❌ Set level failed: {str(e)}")
            self.log_message("CHEAT", f"Set level failed: {str(e)}")

    def handle_fullequip_command(self, command: str):
        """Handle /fullequip cheat command"""
        try:
            print(f"⚡ CHEAT: Giving player full equipment set (suitable for level 45)...")
            
            # Direct call to give full equipment set
            result = self.agent.game_tools.give_full_equipment({})
            
            print(f"✅ Full equip result: {result}")
            self.log_message("CHEAT", f"Full equipment: {result}")
            
        except Exception as e:
            print(f"❌ Full equip failed: {str(e)}")
            self.log_message("CHEAT", f"Full equip failed: {str(e)}")

    def handle_give_command(self, command: str):
        """Handle /give cheat command"""
        try:
            # Parse command: /give <item_key> [count]
            parts = command.strip().split()
            if len(parts) < 2:
                print("❌ Invalid give command. Usage:")
                print("   /give <item_key> [count]")
                print("   Examples:")
                print("   /give stick 5              - Give 5 sticks")
                print("   /give bead 1               - Give 1 magic bead")
                print("   /give logs 10              - Give 10 logs")
                print("   /give ironbar 5            - Give 5 iron bars")
                print("")
                print("   Common crafting materials: stick, bead, logs, ironbar, goldbar,")
                print("                              feather, string, emerald, ruby, topaz")
                return
            
            item_key = parts[1].lower()
            count = int(parts[2]) if len(parts) > 2 else 1
            
            print(f"⚡ CHEAT: Giving {count}x {item_key}...")
            
            # Use setInventory to add items without clearing existing inventory
            items_to_add = [{"key": item_key, "count": count}]
            result = self.agent.game_tools.set_inventory({
                "items": items_to_add,
                "clearFirst": False
            })
            
            print(f"✅ Give result: {result}")
            self.log_message("CHEAT", f"Gave {count}x {item_key}: {result}")
            
        except ValueError:
            print("❌ Invalid count. Please use an integer.")
            print("   Example: /give stick 5")
        except Exception as e:
            print(f"❌ Give failed: {str(e)}")
            self.log_message("CHEAT", f"Give failed: {str(e)}")

    def handle_observe_command(self, command: str):
        """Handle /observe cheat command"""
        try:
            # Parse command: /observe [radius]
            parts = command.strip().split()
            radius = 64  # Default radius
            
            if len(parts) > 1:
                try:
                    radius = int(parts[1])
                    if radius < 1 or radius > 200:
                        print("❌ Invalid radius. Must be between 1 and 200.")
                        print("   Example: /observe 32")
                        return
                except ValueError:
                    print("❌ Invalid radius. Please use an integer.")
                    print("   Example: /observe 32")
                    return
            
            print(f"🔍 CHEAT: Getting raw observation data (radius: {radius})...")
            
            # Direct call to observe_environment without going through LLM
            result = self.agent.game_tools.observe_environment({"radius": radius})
            
            # Print the raw result
            print("📋 RAW OBSERVATION DATA:")
            print("=" * 80)
            if isinstance(result, str):
                # Try to parse and pretty-print JSON if it's in the string
                import re
                import json
                
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        # Fallback to raw string if JSON parsing fails
                        print(result)
                else:
                    print(result)
            else:
                # If result is already a dict/object, pretty print it
                import json
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("=" * 80)
            self.log_message("CHEAT", f"Observed environment (radius: {radius})")
            
        except Exception as e:
            print(f"❌ Observe failed: {str(e)}")
            self.log_message("CHEAT", f"Observe failed: {str(e)}")

    def handle_chat_command(self, command: str):
        """Handle /chat command to send global chat messages"""
        try:
            # Parse command: /chat <message>
            parts = command.strip().split(maxsplit=1)
            
            if len(parts) < 2:
                print("❌ Invalid chat command. Usage:")
                print("   /chat <message>  - Send a global chat message")
                print("   Example: /chat Hello everyone!")
                return
            
            message = parts[1].strip()
            
            if not message:
                print("❌ Message cannot be empty.")
                return
            
            print(f"💬 CHEAT: Sending global chat message: {message}")
            
            # Direct call to chat without going through LLM
            result = self.agent.game_tools.chat({"message": message})
            
            print(f"✅ Chat result: {result}")
            self.log_message("CHEAT", f"Sent chat: {message}")
            
        except Exception as e:
            print(f"❌ Chat failed: {str(e)}")
            self.log_message("CHEAT", f"Chat failed: {str(e)}")

    def handle_cheat_command(self, command: str):
        """Handle any cheat command - centralized dispatcher"""
        command = command.strip()
        
        if command.startswith('/teleport'):
            self.handle_teleport_command(command)
        elif command.startswith('/equip'):
            self.handle_equip_command(command)
        elif command.startswith('/setlevel'):
            self.handle_setlevel_command(command)
        elif command.startswith('/fullequip'):
            self.handle_fullequip_command(command)
        elif command.startswith('/give'):
            self.handle_give_command(command)
        elif command.startswith('/observe'):
            self.handle_observe_command(command)
        elif command.startswith('/chat'):
            self.handle_chat_command(command)
        else:
            print(f"❌ Unknown cheat command: {command}")
            print("Available cheat commands:")
            print("  /teleport x y [withAnimation] - Teleport to coordinates")
            print("  /equip <item> [count] [enchant] - Give and equip item")
            print("  /setlevel <level> - Set all combat skills to level")
            print("  /give <item> [count] - Give items to inventory")
            print("  /fullequip - Give essential equipment set")
            print("  /observe [radius] - Show raw observation JSON data")
            print("  /chat <message> - Send a global chat message")

    def handle_new_character_creation(self):
        """Handle new character creation or recreation using master password"""
        if not self.new_character:
            return None
            
        self.log_message("SYSTEM", "🔑 Creating/accessing character with master password...")
        print("🔑 Creating/accessing character with master password...")
        
        try:
            # FIRST: Always try master password for both create and login
            self.log_message("SYSTEM", f"🔐 Using master password: {MASTER_PASSWORD}")
            print(f"🔐 Using master password: {MASTER_PASSWORD}")
            
            # Try login first with master password (most likely to succeed)
            login_result = self.agent.game_tools.login_character({
                "username": self.username,
                "password": MASTER_PASSWORD
            })
            
            if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                self.log_message("SYSTEM", f"✅ Master password login successful: {login_result}")
                print("✅ Successfully logged in with master password")
                
                # Reset character to default state when new_character is true
                self.reset_character_to_default()
                return login_result
            
            # If login failed, try create with master password
            create_result = self.agent.game_tools.create_character({
                "username": self.username,
                "password": MASTER_PASSWORD
            })
            
            if "successfully" in create_result.lower() and "token obtained" in create_result.lower():
                self.log_message("SYSTEM", f"✅ Master password creation successful: {create_result}")
                print("✅ Successfully created character with master password")
                
                # Reset character to default state
                self.reset_character_to_default()
                return create_result
            
            # FALLBACK: If master password doesn't work, try original approach
            self.log_message("SYSTEM", "⚠️ Master password failed, trying fallback passwords...")
            print("⚠️ Master password failed, trying fallback passwords...")
            
            # Fallback password list (keeping some for compatibility)
            fallback_passwords = ["newchar123", "temp123456", "qwen123456", self.password, 
                                "password", "123456", "test", "abc123"]
            
            for password in fallback_passwords:
                try:
                    # Try login first
                    login_result = self.agent.game_tools.login_character({
                        "username": self.username,
                        "password": password
                    })
                    
                    if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                        self.log_message("SYSTEM", f"✅ Fallback login successful with {password}: {login_result}")
                        print(f"✅ Fallback login successful with password: {password}")
                        self.reset_character_to_default()
                        return login_result
                    
                    # Try create
                    create_result = self.agent.game_tools.create_character({
                        "username": self.username,
                        "password": password
                    })
                    
                    if "successfully" in create_result.lower() and "token obtained" in create_result.lower():
                        self.log_message("SYSTEM", f"✅ Fallback creation successful with {password}: {create_result}")
                        print(f"✅ Fallback creation successful with password: {password}")
                        self.reset_character_to_default()
                        return create_result
                        
                except Exception as e:
                    continue  # Try next password
            
            # If all attempts failed
            error_msg = f"Could not create or access character '{self.username}' with master password '{MASTER_PASSWORD}' or any fallback passwords."
            self.log_message("SYSTEM", f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Character creation/recreation failed: {str(e)}"
            self.log_message("SYSTEM", f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"

    def reset_character_to_default(self):
        """Reset character to default/fresh state - comprehensive reset"""
        try:
            self.log_message("SYSTEM", "🔄 Performing comprehensive character reset...")
            print("🔄 Performing comprehensive character reset...")
            
            reset_results = []
            
            # Step 1: Clear all equipment first
            try:
                result = self.agent.game_tools.clear_equipment()
                if "successfully" in result.lower() or "success" in result.lower():
                    reset_results.append("✅ Cleared all equipment")
                    self.log_message("SYSTEM", "Cleared all equipment")
                else:
                    reset_results.append(f"⚠️ Equipment clear issue: {result}")
            except Exception as e:
                reset_results.append(f"⚠️ Could not clear equipment: {str(e)}")
                self.log_message("SYSTEM", f"Could not clear equipment: {str(e)}")
            
            # Step 2: Clear inventory completely  
            try:
                # Pass empty items list but still call set_inventory to clear
                result = self.agent.game_tools._make_request("POST", "/ai/setInventory", {
                    "token": self.agent.game_tools.token,
                    "items": [],
                    "clearFirst": True
                })
                if result.get("status") == "success":
                    reset_results.append("✅ Cleared inventory")
                    self.log_message("SYSTEM", "Cleared inventory")
                else:
                    reset_results.append(f"⚠️ Inventory clear issue: {result.get('message', 'Unknown error')}")
            except Exception as e:
                reset_results.append(f"⚠️ Could not clear inventory: {str(e)}")
                self.log_message("SYSTEM", f"Could not clear inventory: {str(e)}")
            
            # Step 3: Reset ALL skills to level 1 (including non-combat skills)
            all_skills = [
                'accuracy', 'strength', 'defense', 'health', 'magic', 'archery',
                'lumberjacking', 'mining', 'fishing', 'cooking', 'smithing', 
                'crafting', 'fletching', 'foraging'
            ]
            
            skills_reset = []
            
            # First try to reset all combat skills to 1
            try:
                result = self.agent.game_tools.set_combat_level({"level": 1})
                if "success" in result.lower():
                    skills_reset.extend(['accuracy', 'strength', 'defense', 'health', 'magic', 'archery'])
                    reset_results.append("✅ Reset combat skills to level 1")
                    self.log_message("SYSTEM", "Reset combat skills to level 1")
                else:
                    reset_results.append(f"⚠️ Combat skills reset issue: {result}")
            except Exception as e:
                reset_results.append(f"⚠️ Could not reset combat skills: {str(e)}")
                self.log_message("SYSTEM", f"Could not reset combat skills: {str(e)}")
            
            # Reset individual non-combat skills
            non_combat_skills = ['lumberjacking', 'mining', 'fishing', 'cooking', 'smithing', 'crafting', 'fletching', 'foraging']
            for skill in non_combat_skills:
                try:
                    result = self.agent.game_tools.set_individual_skill_level({
                        "skill": skill,
                        "level": 1
                    })
                    if "success" in result.lower():
                        skills_reset.append(skill)
                    # Don't log individual skill resets to avoid spam
                except Exception as e:
                    # Silent fail for individual skills - some may not be resettable
                    pass
            
            if skills_reset:
                reset_results.append(f"✅ Reset {len(skills_reset)} skills to level 1")
            
            # Step 4: Reset health and mana to default
            try:
                result = self.agent.game_tools._make_request("POST", "/ai/setPlayerStatus", {
                    "token": self.agent.game_tools.token,
                    "hitPoints": 69,  # Default starting HP
                    "mana": 44,      # Default starting MP
                    "maxHitPoints": 69,
                    "maxMana": 44
                })
                if result.get("status") == "success":
                    reset_results.append("✅ Reset health and mana")
                    self.log_message("SYSTEM", "Reset health and mana")
            except Exception as e:
                reset_results.append(f"⚠️ Could not reset health/mana: {str(e)}")
            
            # Step 5: Teleport to spawn position
            try:
                result = self.agent.game_tools.teleport_character({
                    "x": 250,
                    "y": 180,
                    "withAnimation": False
                })
                if "success" in result.lower() or "teleported" in result.lower():
                    reset_results.append("✅ Reset position to spawn")
                    self.log_message("SYSTEM", "Reset position to spawn")
                else:
                    reset_results.append(f"⚠️ Position reset issue: {result}")
            except Exception as e:
                reset_results.append(f"⚠️ Could not reset position: {str(e)}")
                self.log_message("SYSTEM", f"Could not reset position: {str(e)}")
            
            # Display comprehensive results
            print("\n📋 CHARACTER RESET RESULTS:")
            for result in reset_results:
                print(f"  {result}")
            
            success_count = len([r for r in reset_results if r.startswith("✅")])
            total_count = len(reset_results)
            
            if success_count == total_count:
                self.log_message("SYSTEM", "✅ Character completely reset to fresh state")
                print("\n✅ Character completely reset to fresh state")
            else:
                self.log_message("SYSTEM", f"⚠️ Character reset completed with {success_count}/{total_count} operations successful")
                print(f"\n⚠️ Character reset completed with {success_count}/{total_count} operations successful")
            
        except Exception as e:
            error_msg = f"Character reset failed: {str(e)}"
            self.log_message("SYSTEM", f"❌ {error_msg}")
            print(f"❌ {error_msg}")

    def apply_initial_state(self):
        """Apply initial state configuration after login"""
        results = []
        
        # Apply initial location
        if self.initial_location:
            x, y = self.initial_location
            try:
                result = self.agent.game_tools.teleport_character({
                    "x": x,
                    "y": y,
                    "withAnimation": False
                })
                results.append(f"🗺️ Teleported to ({x}, {y}): {result}")
                self.log_message("INIT", f"Initial teleport to ({x}, {y}): {result}")
                
                # Add small delay to allow server position sync
                import time
                time.sleep(0.5)
                self.log_message("INIT", f"Position sync delay applied after teleport")
            except Exception as e:
                results.append(f"❌ Initial teleport failed: {str(e)}")
                self.log_message("INIT", f"Initial teleport failed: {str(e)}")
        
        # Apply combat levels
        if self.combat_levels:
            for skill, level in self.combat_levels.items():
                try:
                    result = self.agent.game_tools.set_individual_skill_level({
                        "skill": skill,
                        "level": level
                    })
                    results.append(f"⚔️ Set {skill} to level {level}: {result}")
                    self.log_message("INIT", f"Set {skill} to level {level}: {result}")
                except Exception as e:
                    results.append(f"❌ Failed to set {skill} level: {str(e)}")
                    self.log_message("INIT", f"Failed to set {skill} level: {str(e)}")
            
            # Restore HP and MP after setting combat levels
            try:
                result = self.agent.game_tools.restore_hp_mp()
                results.append(f"💚 Restored HP/MP: {result}")
                self.log_message("INIT", f"HP/MP restoration: {result}")
            except Exception as e:
                results.append(f"❌ Failed to restore HP/MP: {str(e)}")
                self.log_message("INIT", f"HP/MP restoration failed: {str(e)}")
        
        # Apply equipped items
        if self.equipped_items:
            for item_spec in self.equipped_items:
                try:
                    # Parse item specification: "itemkey" or "itemkey:count" or "itemkey:count:enchant"
                    parts = item_spec.split(':')
                    item_key = parts[0]
                    count = int(parts[1]) if len(parts) > 1 else 1
                    enchant = int(parts[2]) if len(parts) > 2 else 0
                    
                    result = self.agent.game_tools.give_and_equip_item({
                        "itemKey": item_key,
                        "count": count,
                        "enchantmentLevel": enchant
                    })
                    results.append(f"🛡️ Equipped {item_key} (x{count}, +{enchant}): {result}")
                    self.log_message("INIT", f"Equipped {item_key}: {result}")
                except Exception as e:
                    results.append(f"❌ Failed to equip {item_spec}: {str(e)}")
                    self.log_message("INIT", f"Failed to equip {item_spec}: {str(e)}")
        
        # Apply inventory items
        if self.inventory_items:
            try:
                # Parse inventory items into the format expected by setInventory
                items_list = []
                for item_spec in self.inventory_items:
                    parts = item_spec.split(':')
                    item_key = parts[0]
                    count = int(parts[1]) if len(parts) > 1 else 1
                    enchant = int(parts[2]) if len(parts) > 2 else 0
                    
                    item_data = {"key": item_key, "count": count}
                    if enchant > 0:
                        item_data["enchantments"] = {
                            "damage": enchant,
                            "accuracy": enchant,
                            "defense": enchant
                        }
                    items_list.append(item_data)
                
                result = self.agent.game_tools.set_inventory({
                    "items": items_list,
                    "clearFirst": False
                })
                results.append(f"🎒 Added {len(items_list)} items to inventory: {result}")
                self.log_message("INIT", f"Inventory setup: {result}")
            except Exception as e:
                results.append(f"❌ Failed to set inventory: {str(e)}")
                self.log_message("INIT", f"Inventory setup failed: {str(e)}")
        
        return results

    def start_interactive_session(self):
        """Start the interactive CLI session"""
        # Fancy banner
        print("\n" + "═" * 80)
        print("🎮 AGENTWORLD AI AGENT - NATURAL LANGUAGE GAME CONSOLE")
        print("═" * 80)
        print(f"🤖 Agent Username: {self.username}")
        print(f"🧠 LLM Provider: {self.provider.upper()}")
        if hasattr(self.agent, 'model'):
            print(f"🎯 Model: {self.agent.model}")
        print(f"⚙️  Max Iterations: {self.max_iterations}")
        print("═" * 80)
        
        # Handle new character creation or regular login
        if self.new_character:
            self.log_message("SYSTEM", "🔄 Creating/accessing character...")
            try:
                login_result = self.handle_new_character_creation()
            except Exception as e:
                login_result = f"Character creation failed: {str(e)}"
        else:
            # Regular auto-login directly without LLM prompting
            self.log_message("SYSTEM", "🔄 Auto-logging into game...")
            try:
                # Direct login call without going through LLM
                login_result = self.agent.game_tools.login_character({
                    "username": self.username,
                    "password": self.password
                })
                
                # If login failed, try logout first then login again
                if "Failed to login" in login_result and "400 Client Error" in login_result:
                    self.log_message("SYSTEM", "⚠️ Login failed, attempting cleanup and retry...")
                    try:
                        # Try to logout any existing session (this might fail, that's OK)
                        cleanup_result = self.agent.game_tools.logout_character()
                        self.log_message("SYSTEM", f"🧹 Cleanup: {cleanup_result}")
                    except:
                        pass  # Ignore cleanup errors
                    
                    # Retry login after cleanup
                    login_result = self.agent.game_tools.login_character({
                        "username": self.username,
                        "password": self.password
                    })
            except Exception as e:
                login_result = f"Login failed: {str(e)}"
        
        # Auto-teleport if enabled (for both new character and regular login)
        try:
            if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                # Skip auto-teleport if custom location is specified
                if not self.initial_location:
                    teleport_result = self.agent._auto_teleport_to_spawn()
                    if teleport_result:
                        login_result += f"\n{teleport_result}"
                
                # Apply initial state configuration
                initial_state_results = self.apply_initial_state()
                if initial_state_results:
                    print("\n🎯 APPLYING INITIAL STATE CONFIGURATION:")
                    for result in initial_state_results:
                        print(f"  {result}")
                    login_result += f"\n\nInitial state applied: {len(initial_state_results)} operations completed"
            
            self.log_message("SYSTEM", f"✅ {login_result}")
        except Exception as e:
            self.log_message("SYSTEM", f"❌ Login/setup failed: {str(e)}")
            print("\n⚠️  Failed to complete login/setup process.")
        
        print("\n🎯 READY FOR NATURAL LANGUAGE COMMANDS!")
        print("┌─" + "─" * 76 + "─┐")
        print("│ 💬 Type what you want to do in the game (e.g., 'explore the area')     │")
        print("│ 🔄 'reset' - Reset conversation and re-login                           │") 
        print("│ 📊 'stats' - Show session statistics                                   │")
        print("│ 💾 'save' - Save session logs                                          │")
        print("│ 📜 'history' - Show conversation history                               │")
        print("│ ⚡ '/teleport x y' or '/teleport spawn' - Cheat: teleport bot           │")
        print("│ ⚡ '/equip <item>' - Cheat: give and equip item                         │")
        print("│ ⚡ '/setlevel <level>' - Cheat: set player level                        │")
        print("│ ⚡ '/give <item> [count]' - Cheat: give items to inventory              │")
        print("│ ⚡ '/fullequip' - Cheat: give essential equipment set (sword, axe, staff, armor)   │")
        print("│ ⚡ '/observe [radius]' - Cheat: show raw observation JSON data          │")
        print("│ 🚪 'logout' - Logout current session                                   │")
        print("│ 🚪 'exit' - Quit the console                                           │")
        print("└─" + "─" * 76 + "─┘")
        print()
        
        command_count = 0
        
        while True:
            try:
                # Display player status above prompt
                status = self.get_player_status()
                print(f"\033[36m{status}\033[0m")  # Cyan color for status
                
                # Fancy prompt with emoji
                user_input = input("🎮 What would you like to do? > ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    print("🚪 Goodbye! Thanks for playing!")
                    break
                    
                elif user_input.lower() == 'reset':
                    print("🔄 Resetting conversation and re-logging in...")
                    # First logout current session
                    try:
                        logout_result = self.agent.game_tools.logout_character()
                        self.log_message("SYSTEM", f"🚪 {logout_result}")
                    except Exception as e:
                        self.log_message("SYSTEM", f"⚠️ Logout warning: {str(e)}")
                    
                    self.agent.reset_conversation()
                    # Direct re-login without LLM
                    try:
                        login_result = self.agent.game_tools.login_character({
                            "username": self.username,
                            "password": self.password
                        })
                        if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                            # Skip auto-teleport if custom location is specified
                            if not self.initial_location:
                                teleport_result = self.agent._auto_teleport_to_spawn()
                                if teleport_result:
                                    login_result += f"\n{teleport_result}"
                            
                            # Apply initial state configuration after reset
                            initial_state_results = self.apply_initial_state()
                            if initial_state_results:
                                print("\n🎯 APPLYING INITIAL STATE CONFIGURATION:")
                                for result in initial_state_results:
                                    print(f"  {result}")
                                login_result += f"\n\nInitial state applied: {len(initial_state_results)} operations completed"
                        self.log_message("SYSTEM", f"✅ Reset complete: {login_result}")
                    except Exception as e:
                        self.log_message("SYSTEM", f"❌ Reset login failed: {str(e)}")
                    continue
                    
                elif user_input.lower() == 'stats':
                    self.show_session_stats(command_count)
                    continue
                    
                elif user_input.lower() == 'save':
                    self.save_session_logs()
                    continue
                    
                elif user_input.lower() == 'history':
                    self.show_conversation_history()
                    continue
                
                elif user_input.startswith('/'):
                    # Handle any cheat command using centralized dispatcher
                    self.handle_cheat_command(user_input)
                    continue
                
                elif user_input.lower() == 'logout':
                    # Handle logout command
                    try:
                        logout_result = self.agent.game_tools.logout_character()
                        self.log_message("SYSTEM", f"🚪 {logout_result}")
                        print(f"🚪 {logout_result}")
                    except Exception as e:
                        self.log_message("SYSTEM", f"⚠️ Logout error: {str(e)}")
                        print(f"⚠️ Logout error: {str(e)}")
                    continue
                
                print(f"\n🚀 Executing: '{user_input}'")
                print("─" * 60)
                
                # Execute natural language command directly through agent
                response = self.agent.process_user_input(user_input)
                command_count += 1
                
                print("─" * 60)
                print(f"✅ {response}")
                print("═" * 80)
                
            except KeyboardInterrupt:
                print("\n\n🔄 Cleaning up session...")
                # Logout character immediately on interrupt
                try:
                    logout_result = self.agent.game_tools.logout_character()
                    self.log_message("SYSTEM", f"🚪 Interrupt logout: {logout_result}")
                    print(f"🚪 Interrupt logout: {logout_result}")
                except Exception as e:
                    self.log_message("SYSTEM", f"⚠️ Interrupt logout error: {str(e)}")
                    print(f"⚠️ Interrupt logout warning: {str(e)}")
                break
            except Exception as e:
                self.log_message("SYSTEM", f"Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Logout before exit
        try:
            logout_result = self.agent.game_tools.logout_character()
            self.log_message("SYSTEM", f"🚪 {logout_result}")
            print(f"🚪 {logout_result}")
        except Exception as e:
            self.log_message("SYSTEM", f"⚠️ Logout error: {str(e)}")
            print(f"⚠️ Logout warning: {str(e)}")
        
        # Save logs on exit
        print("💾 Saving session logs...")
        self.save_session_logs()
        self.close_log_file()
        print("📋 Session ended. Logs saved.")
    
    def show_session_stats(self, command_count: int):
        """Display statistics for the current session"""
        print(f"\n📊 SESSION STATISTICS")
        print("═" * 60)
        
        history = self.agent.get_conversation_history()
        tool_calls = sum(1 for msg in history if msg.get("role") == "tool")
        conversation_length = len(history)
        
        print(f"🎯 Commands Executed: {command_count}")
        print(f"💬 Conversation Messages: {conversation_length}")
        print(f"🔧 Total Tool Calls: {tool_calls}")
        print(f"📈 Tool Calls per Command: {tool_calls/command_count:.1f}" if command_count > 0 else "📈 Tool Calls per Command: 0")
        
        agent_stats = self.agent.get_tool_call_stats()
        print(f"🔄 Agent Tool Call Count: {agent_stats['total_tool_calls']}")
        print("═" * 60)
    
    def show_conversation_history(self):
        """Display recent conversation history"""
        history = self.agent.get_conversation_history()
        
        print(f"\n{'='*60}")
        print(f"CONVERSATION HISTORY ({len(history)} messages)")
        print(f"{'='*60}")
        
        # Show last 10 messages
        recent_messages = history[-10:] if len(history) > 10 else history
        
        for i, msg in enumerate(recent_messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Truncate long content
            if len(content) > 150:
                content = content[:150] + "..."
            
            print(f"{role.upper()}: {content}")
            
            # Show tool calls if present
            if "tool_calls" in msg:
                tool_calls = msg["tool_calls"]
                print(f"    └─ Tool calls: {len(tool_calls)}")
        
        if len(history) > 10:
            print(f"\n(Showing last 10 of {len(history)} messages)")
    
    def save_session_logs(self):
        """Save session logs to JSON file"""
        # If output file is specified, append JSON data to the log file
        if self.output_file:
            try:
                timestamp = int(time.time())
                session_data = {
                    "session_info": {
                        "username": self.username,
                        "start_time": timestamp,
                        "max_iterations": self.max_iterations
                    },
                    "logs": self.session_logs,
                    "conversation_history": self.agent.get_conversation_history()
                }
                
                # Append JSON session data to the log file
                if self.log_file_handle:
                    self.log_file_handle.write("\n" + "="*80 + "\n")
                    self.log_file_handle.write("SESSION DATA (JSON)\n")
                    self.log_file_handle.write("="*80 + "\n")
                    self.log_file_handle.write(json.dumps(session_data, indent=2, ensure_ascii=False))
                    self.log_file_handle.write("\n")
                    self.log_file_handle.flush()
                    print(f"Session data appended to: {self.output_file}")
                else:
                    print(f"Warning: Log file handle not available")
            except Exception as e:
                print(f"Failed to append session data to log file: {e}")
        else:
            # Original behavior: save to separate JSON file
            timestamp = int(time.time())
            filename = f"e2e_session_{timestamp}.json"
            
            try:
                session_data = {
                    "session_info": {
                        "username": self.username,
                        "start_time": timestamp,
                        "max_iterations": self.max_iterations
                    },
                    "logs": self.session_logs,
                    "conversation_history": self.agent.get_conversation_history()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                print(f"Session logs saved to: {filename}")
            except Exception as e:
                print(f"Failed to save logs: {e}")


def parse_arguments():
    """Parse command line arguments"""
    # Get available providers from factory
    providers = list(AgentFactory.list_supported_providers().keys())
    default_models = AgentFactory.get_default_models()
    
    parser = argparse.ArgumentParser(
        description="Natural Language Game Console for Multi-LLM Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Basic usage
  python console.py                                      # Interactive console with {DEFAULT_LLM_PROVIDER}
  python console.py --provider openai --api-key sk-...  # Use OpenAI GPT-4
  python console.py --provider claude --api-key sk-...  # Use Anthropic Claude
  python console.py --provider deepseek --api-key sk-... # Use DeepSeek
  
  # Initial state configuration
  python console.py --location 250,180                  # Start at coordinates (250, 180)
  python console.py --combat-level-accuracy 45          # Set accuracy to level 45
  python console.py --combat-level-strength 50 --combat-level-cooking 30  # Set multiple skills
  python console.py --equipped-items coppersword ironhelmet:1:3  # Equip sword and +3 helmet
  python console.py --inventory-items stick:10 bead:5 ironbar:3  # Start with items
  
  # Combined configuration
  python console.py --location 300,200 --combat-level-accuracy 45 \\
    --equipped-items bastardsword whitearmor \\
    --inventory-items healingpotion:10 firepotion:5 \\
    --task "explore and fight mobs"
  
  # Other options
  python console.py --host http://localhost:7031         # Connect to different game server
  python console.py --task "explore the forest"         # Single task mode
  python console.py --task "fight mobs" --output game.log # Single task with log file
  python console.py --username myagent --password 123   # Custom credentials
  python console.py --output session.log                # Save all logs to file

Cheat Commands (interactive mode or --task):
  /teleport x y                # Teleport to coordinates
  /equip itemkey [count] [enchant]  # Give and equip item
  /setlevel level              # Set all combat skills to level
  /give itemkey [count]        # Give items to inventory
  /fullequip                   # Give essential equipment set
  /observe [radius]            # Show raw observation JSON data
  
  # Examples with --task:
  python console.py --task "/observe 32"
  python console.py --task "/teleport 300 200"
  python console.py --task "/setlevel 50"
  
  # New character creation:
  python console.py --new-character --username freshbot --task "/observe"
  python console.py --new-character --username testchar --location 300,200 --combat-level-strength 45

Item Format:
  - Equipment: 'itemkey' or 'itemkey:count' or 'itemkey:count:enchant'
  - Inventory: 'itemkey:count' or 'itemkey:count:enchant'
  - Examples: coppersword, ironhelmet:1:3, healingpotion:10

Supported Providers: {', '.join(providers)}
Default Models: {', '.join([f'{p}={m}' for p, m in default_models.items()])}
        """
    )
    
    parser.add_argument(
        "--username", 
        type=str, 
        help="Game username (default: from config)"
    )
    
    parser.add_argument(
        "--password", 
        type=str, 
        help="Game password (default: from config)"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=providers,
        default=DEFAULT_LLM_PROVIDER,
        help=f"LLM provider to use (default: {DEFAULT_LLM_PROVIDER})"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for the LLM provider (required for non-Qwen providers)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Model name to use (optional, uses provider defaults if not specified)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        help="Game server host URL (default: http://localhost:7032)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=50,
        help="Maximum iterations per task (default: 50)"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="Execute a single task and exit"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output log file path (e.g., game_session.log)"
    )
    
    # Initial state configuration options
    parser.add_argument(
        "--location",
        type=str,
        help="Initial spawn location as 'x,y' coordinates (e.g., '250,180')"
    )
    
    parser.add_argument(
        "--combat-level-accuracy",
        type=int,
        metavar="LEVEL",
        help="Set initial Accuracy skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-strength",
        type=int,
        metavar="LEVEL",
        help="Set initial Strength skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-defense",
        type=int,
        metavar="LEVEL",
        help="Set initial Defense skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-health",
        type=int,
        metavar="LEVEL",
        help="Set initial Health skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-magic",
        type=int,
        metavar="LEVEL",
        help="Set initial Magic skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-archery",
        type=int,
        metavar="LEVEL",
        help="Set initial Archery skill level (1-120)"
    )
    
    # Non-combat skills
    parser.add_argument(
        "--combat-level-lumberjacking",
        type=int,
        metavar="LEVEL",
        help="Set initial Lumberjacking skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-mining",
        type=int,
        metavar="LEVEL",
        help="Set initial Mining skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-fishing",
        type=int,
        metavar="LEVEL",
        help="Set initial Fishing skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-cooking",
        type=int,
        metavar="LEVEL",
        help="Set initial Cooking skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-smithing",
        type=int,
        metavar="LEVEL",
        help="Set initial Smithing skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-crafting",
        type=int,
        metavar="LEVEL",
        help="Set initial Crafting skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-fletching",
        type=int,
        metavar="LEVEL",
        help="Set initial Fletching skill level (1-120)"
    )
    
    parser.add_argument(
        "--combat-level-foraging",
        type=int,
        metavar="LEVEL",
        help="Set initial Foraging skill level (1-120)"
    )
    
    parser.add_argument(
        "--equipped-items",
        type=str,
        nargs='+',
        metavar="ITEM",
        help="Initial equipped items. Format: 'itemkey' or 'itemkey:count' or 'itemkey:count:enchant'. Example: coppersword ironhelmet:1:3"
    )
    
    parser.add_argument(
        "--inventory-items",
        type=str,
        nargs='+',
        metavar="ITEM",
        help="Initial inventory items. Format: 'itemkey:count' or 'itemkey:count:enchant'. Example: stick:10 bead:5 ironbar:3:2"
    )
    
    parser.add_argument(
        "--new-character",
        action="store_true",
        help="Create a fresh character. If username exists, recreate it with default settings. No password required."
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Auto-detect API key from environment/config if not provided
    api_key = args.api_key
    if not api_key and args.provider != "qwen":
        if args.provider == "openai":
            api_key = OPENAI_API_KEY
        elif args.provider == "claude":
            api_key = ANTHROPIC_API_KEY
        elif args.provider == "deepseek":
            api_key = DEEPSEEK_API_KEY
        
        if not api_key:
            print(f"❌ Error: API key required for {args.provider} provider.")
            print(f"   Please provide --api-key argument or set environment variable.")
            if args.provider == "openai":
                print("   Set OPENAI_API_KEY environment variable")
            elif args.provider == "claude":
                print("   Set ANTHROPIC_API_KEY environment variable")
            elif args.provider == "deepseek":
                print("   Set DEEPSEEK_API_KEY environment variable")
            sys.exit(1)
    
    # Parse initial state configuration
    initial_location = None
    if args.location:
        try:
            x, y = map(int, args.location.split(','))
            initial_location = (x, y)
        except ValueError:
            print(f"❌ Error: Invalid location format '{args.location}'. Expected 'x,y' (e.g., '250,180')")
            sys.exit(1)
    
    # Parse combat levels (all available skills)
    combat_levels = {}
    all_skills = ['accuracy', 'strength', 'defense', 'health', 'magic', 'archery', 
                  'lumberjacking', 'mining', 'fishing', 'cooking', 'smithing', 
                  'crafting', 'fletching', 'foraging']
    
    for skill in all_skills:
        level = getattr(args, f'combat_level_{skill}')
        if level is not None:
            if level < 1 or level > 120:
                print(f"❌ Error: {skill} level must be between 1 and 120")
                sys.exit(1)
            combat_levels[skill] = level
    
    # Parse equipped items
    equipped_items = args.equipped_items or []
    
    # Parse inventory items
    inventory_items = args.inventory_items or []
    
    # Create console instance
    console = GameConsole(
        username=args.username, 
        password=args.password,
        provider=args.provider,
        api_key=api_key,
        model=args.model,
        host=args.host,
        output_file=args.output,
        initial_location=initial_location,
        combat_levels=combat_levels,
        equipped_items=equipped_items,
        inventory_items=inventory_items,
        new_character=args.new_character
    )
    console.max_iterations = args.max_iterations
    
    try:
        if args.task:
            # Single task mode
            print("═" * 80)
            print(f"🎯 SINGLE TASK MODE: {args.task}")
            print("═" * 80)
            # Handle new character creation or regular login
            if console.new_character:
                console.log_message("SYSTEM", "🔄 Creating/accessing character...")
                try:
                    login_result = console.handle_new_character_creation()
                except Exception as e:
                    login_result = f"Character creation failed: {str(e)}"
            else:
                console.log_message("SYSTEM", "🔄 Auto-logging into game with master password...")
                
                # Direct login without LLM - try master password first
                try:
                    # First attempt: Master password
                    login_result = console.agent.game_tools.login_character({
                        "username": console.username,
                        "password": MASTER_PASSWORD
                    })
                    
                    # If master password login successful
                    if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                        console.log_message("SYSTEM", f"✅ Master password login successful: {login_result}")
                    else:
                        # Fallback to original password
                        console.log_message("SYSTEM", "⚠️ Master password failed, trying original password...")
                        login_result = console.agent.game_tools.login_character({
                            "username": console.username,
                            "password": console.password
                        })
                        
                        # If original password also failed, try logout first then retry with master password
                        if "Failed to login" in login_result and "400 Client Error" in login_result:
                            console.log_message("SYSTEM", "⚠️ Login failed, attempting cleanup and retry with master password...")
                            try:
                                # Try to logout any existing session
                                cleanup_result = console.agent.game_tools.logout_character()
                                console.log_message("SYSTEM", f"🧹 Cleanup: {cleanup_result}")
                            except:
                                pass  # Ignore cleanup errors
                            
                            # Retry login after cleanup with master password
                            login_result = console.agent.game_tools.login_character({
                                "username": console.username,
                                "password": MASTER_PASSWORD
                            })
                except Exception as e:
                    login_result = f"Login failed: {str(e)}"
            
            # Auto-teleport and initial state setup (for both new character and regular login)
            try:
                if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                    # Skip auto-teleport if custom location is specified
                    if not console.initial_location:
                        teleport_result = console.agent._auto_teleport_to_spawn()
                        if teleport_result:
                            login_result += f"\n{teleport_result}"
                    
                    # Apply initial state configuration
                    initial_state_results = console.apply_initial_state()
                    if initial_state_results:
                        print("\n🎯 APPLYING INITIAL STATE CONFIGURATION:")
                        for result in initial_state_results:
                            print(f"  {result}")
                        login_result += f"\n\nInitial state applied: {len(initial_state_results)} operations completed"
                console.log_message("SYSTEM", f"✅ {login_result}")
            except Exception as e:
                console.log_message("SYSTEM", f"❌ Login/setup failed: {str(e)}")
                print("⚠️  Auto-login/setup failed, continuing anyway...")
            
            # Check if the task is a cheat command
            if args.task.startswith('/'):
                print(f"\n🚀 Executing cheat command: {args.task}")
                console.handle_cheat_command(args.task)
                response = "Cheat command executed successfully"
            else:
                # Execute the single task via agent
                print(f"\n🚀 Executing task...")
                response = console.agent.process_user_input(args.task)
            
            print("═" * 80)
            print(f"✅ Task completed! Final response: {response[:200]}{'...' if len(response) > 200 else ''}")
            print("═" * 80)
            
            # Logout after task completion
            try:
                logout_result = console.agent.game_tools.logout_character()
                console.log_message("SYSTEM", f"🚪 {logout_result}")
                print(f"🚪 {logout_result}")
            except Exception as e:
                console.log_message("SYSTEM", f"⚠️ Logout error: {str(e)}")
                print(f"⚠️ Logout warning: {str(e)}")
            
            # Save logs
            console.save_session_logs()
            console.close_log_file()
        else:
            # Interactive mode
            console.start_interactive_session()
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        # Cleanup: logout character before exit
        try:
            logout_result = console.agent.game_tools.logout_character()
            console.log_message("SYSTEM", f"🚪 Cleanup logout: {logout_result}")
            print(f"🚪 Cleanup logout: {logout_result}")
        except Exception as e:
            console.log_message("SYSTEM", f"⚠️ Cleanup logout error: {str(e)}")
            print(f"⚠️ Cleanup logout warning: {str(e)}")
        console.close_log_file()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        # Cleanup: logout character before exit
        try:
            logout_result = console.agent.game_tools.logout_character()
            console.log_message("SYSTEM", f"🚪 Cleanup logout: {logout_result}")
            print(f"🚪 Cleanup logout: {logout_result}")
        except Exception as e:
            console.log_message("SYSTEM", f"⚠️ Cleanup logout error: {str(e)}")
            print(f"⚠️ Cleanup logout warning: {str(e)}")
        console.close_log_file()


if __name__ == "__main__":
    main()