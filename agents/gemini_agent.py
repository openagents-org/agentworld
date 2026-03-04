"""
Gemini Agent for AgentWorld Game
Implements Function Calling using OpenAI-compatible API
"""
import copy
import time
import json
import requests
from typing import Dict, List, Any, Optional
from openai_agent import OpenAIAgent


class GeminiAgent(OpenAIAgent):
    def __init__(self, api_key: str, model: str = "gemini-3-flash-preview", username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None, dump_prompts: bool = False):
        # Initialize parent class (OpenAIAgent -> BaseAgent)
        super().__init__(api_key=api_key, model=model, username=username, password=password, base_url=base_url, dump_prompts=dump_prompts)

        # Override Gemini-specific configuration
        self.api_key = api_key
        self.model = model
        self.base_url = "https://yinli.one/v1"
        self.provider = "gemini"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    @staticmethod
    def _sanitize_tools_for_gemini(tools: List[Dict]) -> List[Dict]:
        """Gemini only supports enum on STRING type. Remove enum from non-string properties."""
        tools = copy.deepcopy(tools)
        for tool in tools:
            func = tool.get("function", {})
            params = func.get("parameters", {})
            for prop in params.get("properties", {}).values():
                if "enum" in prop and prop.get("type") != "string":
                    del prop["enum"]
        return tools

    @staticmethod
    def _fix_tool_message_names(messages: List[Dict]) -> List[Dict]:
        """Gemini requires 'name' on tool response messages. Infer it from the preceding assistant tool_calls."""
        messages = copy.deepcopy(messages)
        # Build map: tool_call_id -> function name from assistant messages
        id_to_name = {}
        for msg in messages:
            if msg.get("role") == "assistant":
                for tc in msg.get("tool_calls", []):
                    tc_id = tc.get("id", "")
                    func_name = tc.get("function", {}).get("name", "")
                    if tc_id and func_name:
                        id_to_name[tc_id] = func_name
        # Add name to tool messages that are missing it
        for msg in messages:
            if msg.get("role") == "tool" and not msg.get("name"):
                tc_id = msg.get("tool_call_id", "")
                if tc_id in id_to_name:
                    msg["name"] = id_to_name[tc_id]
        return messages

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to Gemini model"""
        url = f"{self.base_url}/chat/completions"
        sanitized_tools = self._sanitize_tools_for_gemini(self.tools)
        messages = self._fix_tool_message_names(messages)
        data = {
            "model": self.model,
            "messages": messages,
            "tools": sanitized_tools,
            "tool_choice": "required",
            "parallel_tool_calls": False
        }

        cnt = 0
        last_error = None
        while cnt < 5:
            try:
                response = self.session.post(url, json=data, timeout=120)
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
                print(f"[GEMINI API ERROR] {error_details}", flush=True)
                time.sleep(10 * (cnt + 1))

        return {"error": f"API call failed after 5 attempts: {str(last_error)}"}
