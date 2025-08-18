"""
OpenAI Agent for AgentWorld Game
Implements Function Calling using OpenAI API
"""

import json
import requests
from typing import Dict, List, Any, Optional
from base_agent import BaseAgent


class OpenAIAgent(BaseAgent):
    def __init__(self, api_key: str, model: str = "gpt-4o", username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None, dump_prompts: bool = False):
        # Initialize parent class
        super().__init__(username, password, base_url, dump_prompts)
        
        # OpenAI-specific configuration
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.provider = "openai"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to OpenAI model"""
        url = f"{self.base_url}/chat/completions"
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
    
    def _extract_tool_calls(self, assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from OpenAI response message"""
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