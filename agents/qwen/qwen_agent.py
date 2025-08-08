"""
Qwen AI Agent for Kaetram Game
Implements Function Calling following Alibaba Cloud Qwen documentation
"""

import json
import requests
import time
from typing import Dict, List, Any, Optional
from config import (
    DASHSCOPE_API_KEY,
    QWEN_MODEL, 
    QWEN_BASE_URL,
    AGENT_USERNAME,
    AGENT_PASSWORD,
    SPAWN_POSITION
)
from game_tools import KaetramGameTools
from tool_definitions import get_tool_definitions


class QwenAgent:
    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        self.model = QWEN_MODEL
        self.base_url = QWEN_BASE_URL
        self.game_tools = KaetramGameTools()
        self.tools = get_tool_definitions()
        self.conversation_history = []
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            #"Authorization": "Bearer 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",
            "Content-Type": "application/json"
        })
        
        # Tool call tracking
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
        """Build system prompt for OpenAI compatible mode"""
        system_prompt = """You are an intelligent AI agent that plays the Kaetram MMORPG game. Your goal is to explore, interact, collect resources, and engage with the game world intelligently.

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

        return system_prompt
    
    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to Qwen model"""
        url = f"{QWEN_BASE_URL}/chat/completions"
        # url = "https://api.openai.com/v1/chat/completions"
        data = {
            "model": self.model,
            #"model": "gpt-5",
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto"
            #"parallel_tool_calls": True
        }
        
        try:
            response = self.session.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def _extract_tool_calls(self, assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from OpenAI compatible response message"""
        tool_calls = assistant_message.get("tool_calls", [])
        processed_calls = []
        
        for tool_call in tool_calls:
            try:
                function_info = tool_call.get("function", {})
                name = function_info.get("name", "")
                arguments_str = function_info.get("arguments", "{}")
                
                # Parse arguments JSON string
                arguments = json.loads(arguments_str) if arguments_str else {}
                
                processed_calls.append({
                    "name": name,
                    "arguments": arguments,
                    "id": tool_call.get("id", ""),
                    "type": tool_call.get("type", "function")
                })
            except json.JSONDecodeError as e:
                print(f"Failed to parse tool call arguments: {arguments_str}, error: {e}")
                continue
        
        return processed_calls
    
    def _auto_teleport_to_spawn(self) -> str:
        """Automatically teleport to configured spawn position after login"""
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
            "attack_target": self.game_tools.attack_target
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
        """Process user input and return AI response"""
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user", 
            "content": user_input
        })
        
        # Get AI response
        response = self._make_api_call(self.conversation_history)
        
        if "error" in response:
            return f"Error: {response['error']}"
        
        # Extract assistant message
        choices = response.get("choices", [])
        if not choices:
            return "Error: No response from AI model"
        
        assistant_message = choices[0].get("message", {})
        content = assistant_message.get("content", "")
        
        # Check for tool calls first
        tool_calls = self._extract_tool_calls(assistant_message)
        
        if tool_calls:
            print(f"[ASSISTANT] Response with {len(tool_calls)} tool call(s): {content[:100] if content is not None and len(content) > 100 else content} {'...' if len(content) > 100 else ''}")
        else:
            print(f"[ASSISTANT] Final response: {content[:200] if content is not None and len(content) > 200 else content} {'...' if len(content) > 200 else ''}")
        
        # Add assistant response to conversation (including tool_calls if present)
        assistant_msg = {
            "role": "assistant",
            "content": content
        }
        if tool_calls:
            assistant_msg["tool_calls"] = assistant_message.get("tool_calls", [])
        
        self.conversation_history.append(assistant_msg)
        
        if tool_calls:
            # Execute tool calls and add results to conversation
            print(f"\n[TOOL CALLS] Executing {len(tool_calls)} tool call(s):")
            for i, tool_call in enumerate(tool_calls, 1):
                self.tool_call_count += 1
                function_name = tool_call.get("name", "unknown")
                arguments = tool_call.get("arguments", {})
                print(f"  [{i}] Calling {function_name} with args: {arguments}")
                
                result = self._execute_tool_call(tool_call)
                print(f"  [{i}] Result: {result[:150] if result is not None and len(result) > 150 else result} {'...' if result is not None and len(result) > 150 else ''}")
                
                # Add tool result message following OpenAI format
                self.conversation_history.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call.get("id", "")
                })
            
            # Get AI response after tool execution
            follow_up_response = self._make_api_call(self.conversation_history)
            
            if "error" not in follow_up_response:
                follow_up_choices = follow_up_response.get("choices", [])
                if follow_up_choices:
                    follow_up_message = follow_up_choices[0].get("message", {})
                    follow_up_content = follow_up_message.get("content", "")
                    
                    # Check if follow-up response contains more tool calls
                    follow_up_tool_calls = self._extract_tool_calls(follow_up_message)
                    
                    # Add assistant response to conversation (including tool_calls if present)
                    assistant_msg = {
                        "role": "assistant",
                        "content": follow_up_content
                    }
                    if follow_up_tool_calls:
                        assistant_msg["tool_calls"] = follow_up_message.get("tool_calls", [])
                    
                    self.conversation_history.append(assistant_msg)
                    
                    # If there are more tool calls, continue executing them
                    if follow_up_tool_calls:
                        print(f"\n[FOLLOW-UP TOOL CALLS] Executing {len(follow_up_tool_calls)} additional tool call(s):")
                        for i, tool_call in enumerate(follow_up_tool_calls, 1):
                            self.tool_call_count += 1
                            function_name = tool_call.get("name", "unknown")
                            arguments = tool_call.get("arguments", {})
                            print(f"  [F{i}] Calling {function_name} with args: {arguments}")
                            
                            result = self._execute_tool_call(tool_call)
                            print(f"  [F{i}] Result: {result[:150] if result is not None and len(result) > 150 else result} {'...' if result is not None and len(result) > 150 else ''}")
                            
                            # Add tool result message
                            self.conversation_history.append({
                                "role": "tool",
                                "content": result,
                                "tool_call_id": tool_call.get("id", "")
                            })
                        
                        print(f"[RECURSIVE CALL] Continuing with follow-up response... (Total tools called so far: {self.tool_call_count})")
                        # Recursively call process_user_input to handle any remaining tool calls
                        return self.process_user_input("Continue with your task based on the tool results.")
                    
                    return follow_up_content
            
            print(f"\n[TOOL EXECUTION COMPLETE] Total tools called in this session: {self.tool_call_count}")
            return f"Tool calls executed. {len(tool_calls)} functions were called."
        
        return content
    
    def start_game_session(self) -> str:
        """Start a new game session by logging in"""
        login_prompt = f"Start playing the Kaetram game. Login with username '{AGENT_USERNAME}' and password '{AGENT_PASSWORD}'. If the character doesn't exist, create it first."
        return self.process_user_input(login_prompt)
    
    def auto_play(self, steps: int = 10) -> List[str]:
        """Auto-play the game for a specified number of steps"""
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