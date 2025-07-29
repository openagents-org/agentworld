"""
Qwen AI Agent for Kaetram Game
Implements Function Calling following Alibaba Cloud Qwen documentation
"""

import json
import re
import requests
import time
from typing import Dict, List, Any, Optional
from config import (
    DASHSCOPE_API_KEY,
    QWEN_MODEL, 
    QWEN_BASE_URL,
    AGENT_USERNAME,
    AGENT_PASSWORD
)
from game_tools import KaetramGameTools
from tool_definitions import get_tool_definitions, get_tools_as_string


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
            "Content-Type": "application/json"
        })
        
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
        """Build system prompt with tools information"""
        tools_content = get_tools_as_string()
        
        system_prompt = f"""You are an intelligent AI agent that plays the Kaetram MMORPG game. Your goal is to explore, interact, collect resources, and engage with the game world intelligently.

You have access to various game tools through function calling. Use these tools strategically to:
1. Login or create a character when starting
2. Observe your environment regularly to understand your surroundings  
3. Move around to explore the game world
4. Collect resources when available
5. Interact with other players through chat
6. Engage in combat when appropriate
7. Equip items to improve your character

# Tools

You may call one or more functions to assist with game actions.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{tools_content}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{{"name": "<function-name>", "arguments": <args-json-object>}}
</tool_call>

Always think strategically about your actions. Start by logging in, then observe your environment, and make decisions based on what you see. Be proactive in exploring and engaging with the game world."""

        return system_prompt
    
    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to Qwen model"""
        url = f"{QWEN_BASE_URL}/chat/completions"
        
        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto"
        }
        
        try:
            response = self.session.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def _extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract tool calls from response content"""
        tool_calls = []
        
        # Find all tool_call XML tags
        pattern = r'<tool_call>(.*?)</tool_call>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse JSON content
                tool_call = json.loads(match.strip())
                tool_calls.append(tool_call)
            except json.JSONDecodeError as e:
                print(f"Failed to parse tool call: {match}, error: {e}")
                continue
        
        return tool_calls
    
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
        
        # Add assistant response to conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": content
        })
        
        # Check for tool calls
        tool_calls = self._extract_tool_calls(content)
        
        if tool_calls:
            tool_results = []
            for tool_call in tool_calls:
                result = self._execute_tool_call(tool_call)
                tool_results.append(f"Tool {tool_call.get('name', 'unknown')}: {result}")
            
            # Add tool results to conversation
            tool_results_text = "\n".join(tool_results)
            self.conversation_history.append({
                "role": "user",
                "content": f"Tool execution results:\n{tool_results_text}"
            })
            
            # Get AI response after tool execution
            follow_up_response = self._make_api_call(self.conversation_history)
            
            if "error" not in follow_up_response:
                follow_up_choices = follow_up_response.get("choices", [])
                if follow_up_choices:
                    follow_up_content = follow_up_choices[0].get("message", {}).get("content", "")
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": follow_up_content
                    })
                    return f"{content}\n\n{tool_results_text}\n\n{follow_up_content}"
            
            return f"{content}\n\n{tool_results_text}"
        
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
        self._initialize_system_prompt() 