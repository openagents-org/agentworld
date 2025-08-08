#!/usr/bin/env python3
"""
End-to-End Single Mode Testing Script for Qwen Agent
Allows LLM to execute multi-step actions continuously until task completion.

Usage:
    python e2e_test.py --username <username> --password <password>
    python e2e_test.py --task "Fight the mob until you are level 2"

Example workflow:
User [Fight the mob until you are level 2] -> Assistant [Action] -> Tool Result -> 
Assistant [Action] -> Tool Result -> ... -> Assistant [Response without Action] -> Stop

The agent now automatically handles multi-round tool calls internally,
so the E2E script only needs to continue when there are tool results waiting for response.
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
        self.agent = QwenAgent()
        self.username = username or AGENT_USERNAME
        self.password = password or AGENT_PASSWORD
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
            "INFO": "\033[96m"       # Cyan
        }
        reset_color = "\033[0m"
        
        color = colors.get(message_type, "")
        print(f"{color}[{timestamp}] {message_type}: {content}{reset_color}")
        
        if metadata:
            print(f"    └─ {json.dumps(metadata, indent=6)}")
    
    def has_tool_calls_in_last_response(self, conversation_history: List[Dict]) -> bool:
        """Check if the last assistant response contains tool calls"""
        if not conversation_history:
            return False
            
        # Find the last assistant message
        for msg in reversed(conversation_history):
            if msg.get("role") == "assistant":
                return "tool_calls" in msg
        return False
    
    def should_continue_execution(self, conversation_history: List[Dict]) -> bool:
        """
        Determine if we should continue executing actions based on conversation state
        
        Since the agent now handles multi-round tool calls automatically,
        we only need to continue when there are tool results waiting for response.
        """
        if not conversation_history:
            return False
            
        last_msg = conversation_history[-1]
        
        # If last message is from tool (tool result), we should continue
        # because the agent needs to respond to the tool results
        if last_msg.get("role") == "tool":
            return True
            
        # If last message is assistant without tool_calls, task is complete
        if (last_msg.get("role") == "assistant" and 
            "tool_calls" not in last_msg):
            return False
            
        # If last message is assistant with tool_calls, the agent will handle it automatically
        # so we don't need to continue manually
        return False
    
    def has_pending_tool_results(self, conversation_history: List[Dict]) -> bool:
        """
        Check if there are tool results waiting for AI response.
        This is more efficient than the general should_continue_execution check.
        """
        if not conversation_history:
            return False
            
        # Look for the pattern: tool result -> assistant response
        # If the last message is a tool result, we need to continue
        last_msg = conversation_history[-1]
        return last_msg.get("role") == "tool"
    
    def execute_continuous_task(self, user_prompt: str) -> Dict[str, Any]:
        """
        Execute a user prompt continuously until the AI stops calling tools
        
        The agent now handles multi-round tool calls automatically,
        so we only need to continue when there are tool results waiting for response.
        
        Args:
            user_prompt: The high-level task (e.g., "Fight the mob until you are level 2")
            
        Returns:
            Dictionary containing execution statistics and results
        """
        print(f"\n{'='*80}")
        print(f"EXECUTING CONTINUOUS TASK: {user_prompt}")
        print(f"{'='*80}")
        
        # Initialize execution stats
        stats = {
            "task": user_prompt,
            "start_time": time.time(),
            "iterations": 0,
            "tool_calls": 0,
            "status": "running",
            "final_response": None,
            "conversation_length": 0
        }
        
        # Start the task with initial user prompt
        self.log_message("USER", user_prompt)
        response = self.agent.process_user_input(user_prompt)
        stats["iterations"] += 1
        
        self.log_message("ASSISTANT", response)
        
        # Continue execution loop until AI stops calling tools
        iteration = 1
        while iteration < self.max_iterations:
            conversation_history = self.agent.get_conversation_history()
            stats["conversation_length"] = len(conversation_history)
            
            # Count total tool calls in conversation
            tool_calls = sum(1 for msg in conversation_history if msg.get("role") == "tool")
            stats["tool_calls"] = tool_calls
            
            # Check if there are pending tool results that need AI response
            if not self.has_pending_tool_results(conversation_history):
                stats["status"] = "completed"
                stats["final_response"] = response
                self.log_message("SYSTEM", "Task completed - No pending tool results")
                break
                
            # Continue with follow-up prompt to maintain task focus
            # The agent will automatically handle any remaining tool calls
            follow_up = "Continue with your task based on the previous results."
            self.log_message("SYSTEM", f"Auto-continuing (iteration {iteration + 1})")
            
            response = self.agent.process_user_input(follow_up)
            stats["iterations"] += 1
            
            self.log_message("ASSISTANT", response)
            
            iteration += 1
            time.sleep(0.5)  # Brief pause between iterations
            
        # Finalize execution statistics
        stats["end_time"] = time.time()
        stats["duration"] = stats["end_time"] - stats["start_time"]
        
        if iteration >= self.max_iterations:
            stats["status"] = "max_iterations_reached"
            self.log_message("SYSTEM", f"WARNING: Reached maximum iterations ({self.max_iterations})")
        
        # Print execution summary
        print(f"\n{'='*80}")
        print(f"TASK EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Task: {stats['task']}")
        print(f"Status: {stats['status']}")
        print(f"Duration: {stats['duration']:.2f} seconds")  
        print(f"Iterations: {stats['iterations']}")
        print(f"Tool calls: {stats['tool_calls']}")
        print(f"Conversation length: {stats['conversation_length']} messages")
        print(f"{'='*80}")
        
        return stats
    
    def start_interactive_session(self):
        """Start the interactive CLI session"""
        print("Qwen Agent E2E Testing CLI")
        print("=" * 60)
        print(f"Agent Username: {self.username}")
        print(f"Max Iterations per Task: {self.max_iterations}")
        print("=" * 60)
        
        # Initialize agent session with login
        self.log_message("SYSTEM", "Initializing agent session...")
        login_result = self.agent.start_game_session()
        self.log_message("SYSTEM", f"Login result: {login_result}")
        
        print("\nReady for continuous task execution!")
        print("\nAvailable Commands:")
        print("  - Enter any task prompt to execute continuously")
        print("  - 'reset' to reset conversation history") 
        print("  - 'stats' to show session statistics")
        print("  - 'save' to save session logs")
        print("  - 'history' to show conversation history")
        print("  - 'exit' to quit")
        print()
        
        session_stats = []
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    break
                    
                elif user_input.lower() == 'reset':
                    self.agent.reset_conversation()
                    # Re-login after reset
                    login_result = self.agent.start_game_session()
                    self.log_message("SYSTEM", "Conversation history reset and re-logged in")
                    continue
                    
                elif user_input.lower() == 'stats':
                    self.show_session_stats(session_stats)
                    continue
                    
                elif user_input.lower() == 'save':
                    self.save_session_logs()
                    continue
                    
                elif user_input.lower() == 'history':
                    self.show_conversation_history()
                    continue
                
                # Execute the task continuously
                task_stats = self.execute_continuous_task(user_input)
                session_stats.append(task_stats)
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                self.log_message("SYSTEM", f"Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Save logs on exit
        self.save_session_logs()
        print("\nSession ended. Logs saved.")
    
    def show_session_stats(self, session_stats: List[Dict]):
        """Display statistics for the current session"""
        if not session_stats:
            print("No tasks executed in this session yet.")
            return
            
        print(f"\n{'='*60}")
        print(f"SESSION STATISTICS ({len(session_stats)} tasks)")
        print(f"{'='*60}")
        
        total_duration = sum(s["duration"] for s in session_stats)
        total_iterations = sum(s["iterations"] for s in session_stats)
        total_tool_calls = sum(s["tool_calls"] for s in session_stats)
        completed_tasks = sum(1 for s in session_stats if s["status"] == "completed")
        
        print(f"Total Tasks: {len(session_stats)}")
        print(f"Completed: {completed_tasks}")
        print(f"Success Rate: {completed_tasks/len(session_stats)*100:.1f}%")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"Total Iterations: {total_iterations}")
        print(f"Total Tool Calls: {total_tool_calls}")
        print(f"Avg Duration/Task: {total_duration/len(session_stats):.2f} seconds")
        
        print(f"\nRECENT TASKS:")
        for i, stats in enumerate(session_stats[-5:], 1):
            status_emoji = "✅" if stats["status"] == "completed" else "❌"
            task_preview = stats['task'][:50] + "..." if len(stats['task']) > 50 else stats['task']
            print(f"  {status_emoji} {task_preview} ({stats['duration']:.1f}s, {stats['iterations']} iter)")
    
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
        description="End-to-End Single Mode Testing for Qwen Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python e2e_test.py                                    # Interactive mode
  python e2e_test.py --task "Fight mobs until level 2" # Single task mode
  python e2e_test.py --username myagent --password 123 # Custom credentials
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
            print(f"Executing single task: {args.task}")
            cli.log_message("SYSTEM", "Initializing for single task execution...")
            
            # Initialize session with login
            login_result = cli.agent.start_game_session()
            cli.log_message("SYSTEM", f"Login result: {login_result}")
            
            # Execute the continuous task
            result = cli.execute_continuous_task(args.task)
            print(f"\nSingle task execution completed with status: {result['status']}")
            
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