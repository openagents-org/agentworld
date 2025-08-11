"""
Anthropic Claude Agent for AgentWorld Game
Implements Function Calling using Anthropic Claude API
"""

import json
import requests
from typing import Dict, List, Any, Optional
from base_agent import BaseAgent


class ClaudeAgent(BaseAgent):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None):
        # Initialize parent class
        super().__init__(username, password, base_url)
        
        # Claude-specific configuration
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        })

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to Claude model"""
        url = f"{self.base_url}/messages"
        
        # Convert messages to Claude format
        claude_messages = []
        system_message = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "tool":
                # Claude expects tool_use messages as user messages with tool_result content
                claude_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.get("tool_call_id", ""),
                            "content": msg["content"]
                        }
                    ]
                })
            elif msg["role"] == "assistant" and "tool_calls" in msg:
                # Convert OpenAI tool calls to Claude tool_use format
                content = []
                if msg.get("content"):
                    content.append({"type": "text", "text": msg["content"]})
                
                for tool_call in msg["tool_calls"]:
                    function_info = tool_call.get("function", {})
                    content.append({
                        "type": "tool_use",
                        "id": tool_call.get("id", ""),
                        "name": function_info.get("name", ""),
                        "input": json.loads(function_info.get("arguments", "{}"))
                    })
                
                claude_messages.append({
                    "role": "assistant",
                    "content": content
                })
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Convert tools to Claude format
        claude_tools = []
        for tool in self.tools:
            claude_tools.append({
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"]
            })
        
        data = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": claude_messages,
            "tools": claude_tools
        }
        
        if system_message:
            data["system"] = system_message
        
        try:
            response = self.session.post(url, json=data, timeout=60)
            response.raise_for_status()
            claude_response = response.json()
            
            # Convert Claude response to OpenAI format
            return self._convert_claude_response_to_openai(claude_response)
        except requests.exceptions.RequestException as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def _convert_claude_response_to_openai(self, claude_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Claude response format to OpenAI format for compatibility"""
        content_blocks = claude_response.get("content", [])
        
        # Extract text content and tool uses
        text_content = ""
        tool_calls = []
        
        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append({
                    "id": block.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": block.get("name", ""),
                        "arguments": json.dumps(block.get("input", {}))
                    }
                })
        
        message = {
            "role": "assistant",
            "content": text_content
        }
        
        if tool_calls:
            message["tool_calls"] = tool_calls
        
        return {
            "choices": [{"message": message}],
            "usage": claude_response.get("usage", {})
        }
    
    def _extract_tool_calls(self, assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from Claude response message (already converted to OpenAI format)"""
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