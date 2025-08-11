"""
Abstract Base Agent for AgentWorld Game
Defines the interface that all LLM provider agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from game_tools import KaetramGameTools
from tool_definitions import get_tool_definitions


class BaseAgent(ABC):
    """Abstract base class for all LLM provider agents"""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None):
        self.game_tools = KaetramGameTools(base_url=base_url)
        self.tools = get_tool_definitions()
        self.conversation_history = []
        self.username = username
        self.password = password
        self.tool_call_count = 0
        
        # Initialize with system prompt
        self._initialize_system_prompt()
    
    def _initialize_system_prompt(self):
        """Initialize the conversation with system prompt"""
        system_prompt = self._build_system_prompt()
        self.conversation_history = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the agent"""
        return """You are an intelligent AI agent that plays the AgentWorld MMORPG game. Your goal is to explore, interact, collect resources, and engage with the game world intelligently.

You have access to various game tools through function calling. Use these tools strategically to:
1. Login or create a character when starting
2. Observe your environment regularly to understand your surroundings  
3. Move around to explore the game world
4. Collect resources when available
5. Interact with other players through chat
6. Engage in combat when appropriate
7. Equip items to improve your character

Always think strategically about your actions. Start by logging in, then observe your environment, and make decisions based on what you see. Be proactive in exploring and engaging with the game world.
"""
    
    @abstractmethod
    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to the LLM provider. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _extract_tool_calls(self, assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from the LLM response. Must be implemented by subclasses."""
        pass
    
    def _auto_teleport_to_spawn(self) -> str:
        """Automatically teleport to configured spawn position after login"""
        from config import SPAWN_POSITION
        
        if not SPAWN_POSITION.get("enabled", False):
            return ""
        
        if not self.game_tools.token:
            return ""
        
        x = SPAWN_POSITION.get("x", 250)
        y = SPAWN_POSITION.get("y", 180) 
        with_animation = SPAWN_POSITION.get("withAnimation", False)
        
        try:
            result = self.game_tools.teleport_character({
                "x": x,
                "y": y,
                "withAnimation": with_animation
            })
            return f"Auto-teleported to spawn position: {result}"
        except Exception as e:
            return f"Failed to teleport to spawn position: {str(e)}"

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Execute a tool call and return the result"""
        function_name = tool_call.get("name", "")
        arguments = tool_call.get("arguments", {})
        
        # Map function names to game tools methods
        tool_mapping = {
            "create_character": self.game_tools.create_character,
            "login_character": self.game_tools.login_character,
            "move_character": self.game_tools.move_character,
            "send_chat_message": self.game_tools.send_chat_message,
            "observe_environment": self.game_tools.observe_environment,
            "enter_portal": self.game_tools.enter_portal,
            "stop_action": self.game_tools.stop_action,
            "equip_item": self.game_tools.equip_item,
            "collect_resource": self.game_tools.collect_resource,
            "target_entity": self.game_tools.target_entity,
            "attack_target": self.game_tools.attack_target,
            "set_combat_level": self.game_tools.set_combat_level
        }
        
        if function_name in tool_mapping:
            try:
                result = tool_mapping[function_name](arguments)
                
                # Auto-teleport to spawn position after successful login or character creation
                if function_name in ["login_character", "create_character"]:
                    if "successfully" in result.lower() and "token obtained" in result.lower():
                        teleport_result = self._auto_teleport_to_spawn()
                        if teleport_result:
                            result += f"\n{teleport_result}"
                
                return result
            except Exception as e:
                return f"Error executing {function_name}: {str(e)}"
        else:
            return f"Unknown tool: {function_name}"
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return AI response.

        This method will loop, executing tool calls and querying the model
        until the model returns a final assistant message without tool calls.
        """
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        max_rounds = 20  # safety cap to avoid infinite tool-call loops
        rounds = 0
        final_content: str = ""

        while rounds < max_rounds:
            rounds += 1

            response = self._make_api_call(self.conversation_history)
            if "error" in response:
                return f"Error: {response['error']}"

            choices = response.get("choices", [])
            if not choices:
                return "Error: No response from AI model"

            assistant_message = choices[0].get("message", {})
            content = assistant_message.get("content") or ""
            tool_calls = self._extract_tool_calls(assistant_message)

            if tool_calls:
                print(f"\033[90m[ASSISTANT] Response with {len(tool_calls)} tool call(s): {content[:100]}{'...' if len(content) > 100 else ''}\033[0m")
            else:
                print(f"\033[92m[ASSISTANT] Final response: {content[:200]}{'...' if len(content) > 200 else ''}\033[0m")

            # Add assistant message (include original tool_calls if present)
            assistant_msg: Dict[str, Any] = {
                "role": "assistant",
                "content": content
            }
            if tool_calls:
                assistant_msg["tool_calls"] = assistant_message.get("tool_calls", [])
            self.conversation_history.append(assistant_msg)

            # If no tool calls, we are done
            if not tool_calls:
                final_content = content
                break

            # Execute tool calls and append tool result messages
            print(f"\n\033[90m[TOOL CALLS] Executing {len(tool_calls)} tool call(s):\033[0m")
            for index, tool_call in enumerate(tool_calls, 1):
                self.tool_call_count += 1
                function_name = tool_call.get("name", "unknown")
                arguments = tool_call.get("arguments", {})
                print(f"\033[90m  [{index}] Calling {function_name} with args: {arguments}\033[0m")

                result = self._execute_tool_call(tool_call)
                preview = (result or "")
                print(f"\033[90m  [{index}] Result: {preview[:150]}{'...' if len(preview) > 150 else ''}\033[0m")

                self.conversation_history.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call.get("id", "")
                })

            # Continue loop to let the model consume tool results and decide next step
            print(f"\033[90m[TOOL EXECUTION] Round {rounds} completed, continuing...\033[0m")

        if rounds >= max_rounds:
            warning_msg = f"Stopped after {max_rounds} rounds to avoid infinite loop."
            print(f"\033[91m⚠️  {warning_msg}\033[0m")
            return warning_msg

        print(f"\033[90m[TOOL EXECUTION] Completed after {rounds} round(s)\033[0m")
        return final_content
    
    def start_game_session(self, username: Optional[str] = None, password: Optional[str] = None) -> str:
        """Start a new game session by logging in with provided or default credentials."""
        if username:
            self.username = username
        if password:
            self.password = password
        login_prompt = (
            f"Start playing the AgentWorld game. Login with username '{self.username}' and password '{self.password}'. "
            f"If the character doesn't exist, create it first."
        )
        return self.process_user_input(login_prompt)
    
    def auto_play(self, steps: int = 10) -> List[str]:
        """Auto-play the game for a specified number of steps"""
        import time
        
        responses = []
        
        # Start session
        start_response = self.start_game_session()
        responses.append(f"Session Start: {start_response}")
        
        auto_play_prompts = [
            "Observe your current environment to understand where you are and what's around you.",
            "Based on your observations, decide on your next action. You could explore, collect resources, or interact with entities.",
            "Continue exploring the game world. Move to an interesting location or interact with something you observed.",
            "Look for resources to collect or enemies to fight. Take appropriate action based on what you find.",
            "Check your inventory and equipment. Equip any useful items you might have.",
            "Send a friendly chat message to other players in the area.",
            "Continue your adventure by exploring new areas or engaging in activities that help your character progress."
        ]
        
        for i in range(min(steps, len(auto_play_prompts))):
            prompt = auto_play_prompts[i]
            response = self.process_user_input(prompt)
            responses.append(f"Step {i+1}: {response}")
            time.sleep(2)  # Brief pause between actions
        
        return responses
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history"""
        return self.conversation_history
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.tool_call_count = 0
        self._initialize_system_prompt()
    
    def get_tool_call_stats(self) -> Dict[str, Any]:
        """Get tool call statistics"""
        return {
            "total_tool_calls": self.tool_call_count,
            "conversation_length": len(self.conversation_history),
            "tool_results": sum(1 for msg in self.conversation_history if msg.get("role") == "tool")
        }