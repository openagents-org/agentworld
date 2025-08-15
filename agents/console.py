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
<<<<<<< HEAD
    python console.py --host http://localhost:9001                 # Connect to different game server
    python console.py --task "Fight mobs until level 2"           # Single task mode
    python console.py --username myagent --password 123           # Custom credentials
=======
    python console.py --task "Fight mobs until level 2"           # Single task mode
    python console.py --task "explore" --output game.log          # Single task with log output
    python console.py --username myagent --password 123           # Custom credentials
    python console.py --output session.log                        # Interactive mode with log file
>>>>>>> origin/rebuild

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
        host: str = None
        output_file: str = None
    ):
        # Pass credentials to agent so it can use them for login prompts
        self.username = username or AGENT_USERNAME
        self.password = password or AGENT_PASSWORD
        self.provider = provider or DEFAULT_LLM_PROVIDER
        self.api_key = api_key
        self.model = model
        self.host = host
        self.output_file = output_file
        
        # Create the appropriate agent using the factory
        try:
            self.agent = AgentFactory.create_agent(
                provider=self.provider,
                api_key=self.api_key,
                model=self.model,
                username=self.username,
                password=self.password,
                base_url=self.host
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
        
        # Auto-login directly without LLM prompting
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
            
            # Auto-teleport if enabled
            if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                teleport_result = self.agent._auto_teleport_to_spawn()
                if teleport_result:
                    login_result += f"\n{teleport_result}"
            
            self.log_message("SYSTEM", f"✅ {login_result}")
        except Exception as e:
            self.log_message("SYSTEM", f"❌ Login failed: {str(e)}")
            print("\n⚠️  Failed to auto-login. You may need to login manually in your first command.")
        
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
                            teleport_result = self.agent._auto_teleport_to_spawn()
                            if teleport_result:
                                login_result += f"\n{teleport_result}"
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
                
                elif user_input.startswith('/teleport'):
                    # Handle teleport cheat command
                    self.handle_teleport_command(user_input)
                    continue
                
                elif user_input.startswith('/equip'):
                    # Handle equip cheat command
                    self.handle_equip_command(user_input)
                    continue
                
                elif user_input.startswith('/setlevel'):
                    # Handle setlevel cheat command
                    self.handle_setlevel_command(user_input)
                    continue
                
                elif user_input.startswith('/fullequip'):
                    # Handle fullequip cheat command
                    self.handle_fullequip_command(user_input)
                    continue
                
                elif user_input.startswith('/give'):
                    # Handle give item cheat command
                    self.handle_give_command(user_input)
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
  python console.py                                      # Interactive console with {DEFAULT_LLM_PROVIDER}
  python console.py --provider openai --api-key sk-...  # Use OpenAI GPT-4
  python console.py --provider claude --api-key sk-...  # Use Anthropic Claude
  python console.py --provider deepseek --api-key sk-... # Use DeepSeek
  python console.py --host http://localhost:9001         # Connect to different game server
  python console.py --task "explore the forest"         # Single task mode
  python console.py --task "fight mobs" --output game.log # Single task with log file
  python console.py --username myagent --password 123   # Custom credentials
  python console.py --output session.log                # Save all logs to file

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
    
    # Create console instance
    console = GameConsole(
        username=args.username, 
        password=args.password,
        provider=args.provider,
        api_key=api_key,
        model=args.model,
        host=args.host
        output_file=args.output
    )
    console.max_iterations = args.max_iterations
    
    try:
        if args.task:
            # Single task mode
            print("═" * 80)
            print(f"🎯 SINGLE TASK MODE: {args.task}")
            print("═" * 80)
            console.log_message("SYSTEM", "🔄 Auto-logging into game...")
            
            # Direct login without LLM
            try:
                login_result = console.agent.game_tools.login_character({
                    "username": console.username,
                    "password": console.password
                })
                
                # If login failed, try logout first then login again
                if "Failed to login" in login_result and "400 Client Error" in login_result:
                    console.log_message("SYSTEM", "⚠️ Login failed, attempting cleanup and retry...")
                    try:
                        # Try to logout any existing session
                        cleanup_result = console.agent.game_tools.logout_character()
                        console.log_message("SYSTEM", f"🧹 Cleanup: {cleanup_result}")
                    except:
                        pass  # Ignore cleanup errors
                    
                    # Retry login after cleanup
                    login_result = console.agent.game_tools.login_character({
                        "username": console.username,
                        "password": console.password
                    })
                
                if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                    teleport_result = console.agent._auto_teleport_to_spawn()
                    if teleport_result:
                        login_result += f"\n{teleport_result}"
                console.log_message("SYSTEM", f"✅ {login_result}")
            except Exception as e:
                console.log_message("SYSTEM", f"❌ Login failed: {str(e)}")
                print("⚠️  Auto-login failed, continuing anyway...")
            
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
        console.close_log_file()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        console.close_log_file()


if __name__ == "__main__":
    main()