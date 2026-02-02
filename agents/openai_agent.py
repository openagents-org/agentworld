"""
OpenAI Agent for AgentWorld Game
Implements Function Calling using OpenAI API
"""
import time
import json
import requests
from typing import Dict, List, Any, Optional
from base_agent import BaseAgent


class OpenAIAgent(BaseAgent):
    def __init__(self, api_key: str, model: str = "gpt-4o", username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None, dump_prompts: bool = False):
        # Initialize parent class
        super().__init__(username, password, base_url, dump_prompts)
        
        # OpenAI-specific configuration
        self.api_key = api_key or 'agentworld'
        self.model = model
        self.base_url = "https://model-gateway.acenta.ai/v1"
        self.provider = "openai"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to OpenAI model"""
        url = f"{self.base_url}/chat/completions"
        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "required",  # Force model to always call a tool (prevents thinking loops)
            "parallel_tool_calls": False
        }

        cnt = 0
        last_error = None
        while cnt < 5:
            try:
                response = self.session.post(url, json=data, timeout=60)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                cnt += 1
                last_error = e
                error_details = f"Attempt {cnt}/5 failed: {type(e).__name__}: {str(e)}"
                status_code = None
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    error_details += f" | Status: {status_code} | Body: {e.response.text[:500]}"
                print(f"[API ERROR] {error_details}", flush=True)

                # Save request payload for 520 errors (CloudFlare server errors)
                if status_code == 520:
                    import os
                    from datetime import datetime
                    error_dir = os.path.join(os.path.dirname(__file__), "error_captures")
                    os.makedirs(error_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    error_file = os.path.join(error_dir, f"520_error_{timestamp}.json")
                    with open(error_file, 'w') as f:
                        json.dump({
                            "timestamp": timestamp,
                            "error": str(e),
                            "status_code": status_code,
                            "request_data": data
                        }, f, indent=2, default=str)
                    print(f"[API ERROR] Saved 520 error payload to: {error_file}", flush=True)

                time.sleep(10 * (cnt + 1))

        return {"error": f"API call failed after 5 attempts: {str(last_error)}"}
    
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