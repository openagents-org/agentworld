"""
Anthropic Claude Agent for AgentWorld Game
Implements Function Calling using Anthropic Claude API
"""

import json
import requests
from typing import Dict, List, Any, Optional
from base_agent import BaseAgent


class ClaudeAgent(BaseAgent):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None, dump_prompts: bool = False):
        # Initialize parent class
        super().__init__(username, password, base_url, dump_prompts)
        
        # Claude-specific configuration (using model gateway)
        self.api_key = api_key or 'agentworld'
        self.model = model
        self.base_url = "https://model-gateway.acenta.ai/v1"
        self.provider = "claude"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to Claude model via OpenAI-compatible gateway"""
        url = f"{self.base_url}/chat/completions"
        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "required",  # Force model to always call a tool (prevents thinking loops)
            "max_tokens": 4096
        }

        try:
            response = self.session.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                    print(f"\n❌ CLAUDE API ERROR: {e}")
                    print(f"❌ RESPONSE BODY: {error_detail}\n")
                except:
                    pass
            return {"error": f"API call failed: {str(e)} Response: {error_detail}"}
    
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