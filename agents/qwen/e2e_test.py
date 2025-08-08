#!/usr/bin/env python3
"""
Natural Language Game Console for Qwen Agent
Interactive CLI that allows players to control the game agent using natural language.

Usage:
    python e2e_test.py --username <username> --password <password>  # Interactive mode
    python e2e_test.py --task "Fight mobs until level 2"            # Single task mode

Features:
- Auto-login without prompting the LLM
- Direct natural language commands (e.g., "explore the area", "collect resources")
- Fancy console interface with emojis
- Session statistics and conversation history
- Automatic tool call execution until task completion

The agent handles multi-round tool calls internally and stops when no more tools are needed.
"""

import argparse
import json
import time
import sys
from typing import List, Dict, Any, Optional
from qwen_agent import QwenAgent
from config import AGENT_USERNAME, AGENT_PASSWORD


class E2ETestCLI:
    def __init__(self, username: str = None, password: str = None):
        # Pass credentials to agent so it can use them for login prompts
        self.username = username or AGENT_USERNAME
        self.password = password or AGENT_PASSWORD
        self.agent = QwenAgent(username=self.username, password=self.password)
        self.max_iterations = 50  # Safety limit to prevent infinite loops
        self.session_logs = []
        
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
        
        # Color coding for different message types
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

    def start_interactive_session(self):
        """Start the interactive CLI session"""
        # Fancy banner
        print("\n" + "═" * 80)
        print("🎮 AGENTWORLD AI AGENT - NATURAL LANGUAGE GAME CONSOLE")
        print("═" * 80)
        print(f"🤖 Agent Username: {self.username}")
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
            
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"Session logs saved to: {filename}")
        except Exception as e:
            print(f"Failed to save logs: {e}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Natural Language Game Console for Qwen Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python e2e_test.py                                      # Interactive console
  python e2e_test.py --task "explore the forest"         # Single task mode
  python e2e_test.py --username myagent --password 123   # Custom credentials
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
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Create CLI instance
    cli = E2ETestCLI(username=args.username, password=args.password)
    cli.max_iterations = args.max_iterations
    
    try:
        if args.task:
            # Single task mode
            print("═" * 80)
            print(f"🎯 SINGLE TASK MODE: {args.task}")
            print("═" * 80)
            cli.log_message("SYSTEM", "🔄 Auto-logging into game...")
            
            # Direct login without LLM
            try:
                login_result = cli.agent.game_tools.login_character({
                    "username": cli.username,
                    "password": cli.password
                })
                
                # If login failed, try logout first then login again
                if "Failed to login" in login_result and "400 Client Error" in login_result:
                    cli.log_message("SYSTEM", "⚠️ Login failed, attempting cleanup and retry...")
                    try:
                        # Try to logout any existing session
                        cleanup_result = cli.agent.game_tools.logout_character()
                        cli.log_message("SYSTEM", f"🧹 Cleanup: {cleanup_result}")
                    except:
                        pass  # Ignore cleanup errors
                    
                    # Retry login after cleanup
                    login_result = cli.agent.game_tools.login_character({
                        "username": cli.username,
                        "password": cli.password
                    })
                
                if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                    teleport_result = cli.agent._auto_teleport_to_spawn()
                    if teleport_result:
                        login_result += f"\n{teleport_result}"
                cli.log_message("SYSTEM", f"✅ {login_result}")
            except Exception as e:
                cli.log_message("SYSTEM", f"❌ Login failed: {str(e)}")
                print("⚠️  Auto-login failed, continuing anyway...")
            
            # Execute the single task via agent
            print(f"\n🚀 Executing task...")
            response = cli.agent.process_user_input(args.task)
            
            print("═" * 80)
            print(f"✅ Task completed! Final response: {response[:200]}{'...' if len(response) > 200 else ''}")
            print("═" * 80)
            
            # Logout after task completion
            try:
                logout_result = cli.agent.game_tools.logout_character()
                cli.log_message("SYSTEM", f"🚪 {logout_result}")
                print(f"🚪 {logout_result}")
            except Exception as e:
                cli.log_message("SYSTEM", f"⚠️ Logout error: {str(e)}")
                print(f"⚠️ Logout warning: {str(e)}")
            
            # Save logs
            cli.save_session_logs()
        else:
            # Interactive mode
            cli.start_interactive_session()
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()