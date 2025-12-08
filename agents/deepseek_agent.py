"""
DeepSeek Agent for AgentWorld Game
Implements Function Calling using DeepSeek API
For models without native tool support, uses JSON-based tool calling
"""

import json
import re
import requests
import uuid
import time
from typing import Dict, List, Any, Optional
from base_agent import BaseAgent


class DeepSeekAgent(BaseAgent):
    def __init__(self, api_key: str, model: str = "deepseek-chat", username: Optional[str] = None, password: Optional[str] = None, base_url: Optional[str] = None, dump_prompts: bool = False):
        # Initialize parent class
        super().__init__(username, password, base_url, dump_prompts)

        # DeepSeek-specific configuration (using model gateway)
        self.api_key = api_key or 'agentworld'
        self.model = model
        self.base_url = "https://model-gateway.acenta.ai/v1"
        self.provider = "deepseek"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })

        # Check if model supports native tool calling
        self.supports_native_tools = not self.model.startswith("deepseek-r1")

    def _get_tools_description_for_prompt(self) -> str:
        """Generate a text description of available tools for JSON-based calling"""
        tools_desc = []
        for tool in self.tools:
            func = tool["function"]
            params = func.get("parameters", {}).get("properties", {})
            required = func.get("parameters", {}).get("required", [])

            param_desc = []
            for param_name, param_info in params.items():
                req_marker = "(required)" if param_name in required else "(optional)"
                param_desc.append(f"    - {param_name}: {param_info.get('type', 'any')} {req_marker} - {param_info.get('description', '')}")

            tools_desc.append(f"""
- **{func['name']}**: {func['description']}
  Parameters:
{chr(10).join(param_desc) if param_desc else '    (no parameters)'}""")

        return "\n".join(tools_desc)

    def _inject_json_tool_instructions(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Inject instructions for JSON-based tool calling into the system prompt"""
        tools_description = self._get_tools_description_for_prompt()

        json_instructions = f"""

=== IMPORTANT: TOOL CALLING FORMAT ===
You MUST call tools by outputting a JSON block in this EXACT format. Output ONLY the JSON block, nothing else:

```json
{{
  "tool": "tool_name",
  "arguments": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}
```

CRITICAL RULES:
1. You MUST output exactly ONE tool call per response
2. Output ONLY the JSON block - no explanation, no text before or after
3. The JSON must be valid and parseable
4. Use the exact tool names and parameter names listed below

=== AVAILABLE TOOLS ===
{tools_description}

=== EXAMPLE TOOL CALLS ===

To move to coordinates (100, 200):
```json
{{"tool": "move_character", "arguments": {{"x": 100, "y": 200}}}}
```

To send a chat message:
```json
{{"tool": "send_chat_message", "arguments": {{"message": "Hello team!", "global": true}}}}
```

To harvest a resource:
```json
{{"tool": "harvest_resource", "arguments": {{"targetInstance": "12345"}}}}
```

To attack an entity:
```json
{{"tool": "attack_entity", "arguments": {{"targetInstance": "67890"}}}}
```

To complete the task:
```json
{{"tool": "complete", "arguments": {{"summary": "Task completed successfully"}}}}
```

Remember: Output ONLY the JSON block for the tool call. No other text!
"""

        modified_messages = []
        for msg in messages:
            if msg["role"] == "system":
                modified_messages.append({
                    "role": "system",
                    "content": msg["content"] + json_instructions
                })
            else:
                modified_messages.append(msg)

        return modified_messages

    def _parse_json_tool_call(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse JSON tool call from model response"""
        if not content:
            return None

        # Try to find JSON block in markdown code fence
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON object
        json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Try to parse the entire content as JSON
        try:
            parsed = json.loads(content.strip())
            if isinstance(parsed, dict) and "tool" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

        return None

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make API call to DeepSeek model"""
        url = f"{self.base_url}/chat/completions"

        if self.supports_native_tools:
            # Use native tool calling
            data = {
                "model": self.model,
                "messages": messages,
                "tools": self.tools,
                "tool_choice": "auto",
                "max_tokens": 4096
            }
        else:
            # Use JSON-based tool calling
            modified_messages = self._inject_json_tool_instructions(messages)
            data = {
                "model": self.model,
                "messages": modified_messages,
                "max_tokens": 4096
            }

        cnt = 0
        last_error = ""
        while cnt < 5:
            try:
                response = self.session.post(url, json=data, timeout=120)
                response.raise_for_status()
                result = response.json()

                # If using JSON-based tools, convert response to tool call format
                if not self.supports_native_tools:
                    result = self._convert_json_response_to_tool_calls(result)

                return result
            except requests.exceptions.RequestException as e:
                cnt += 1
                error_detail = ""
                if getattr(e, "response", None) is not None:
                    try:
                        error_detail = e.response.text
                        print(f"\n❌ DEEPSEEK API ERROR: {e}")
                        print(f"❌ RESPONSE BODY: {error_detail}\n")
                    except Exception:
                        pass
                last_error = f"{str(e)} Response: {error_detail}"
                time.sleep(10 * (cnt + 1))

        return {"error": f"API call failed: {last_error}"}

    def _convert_json_response_to_tool_calls(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON-based response to standard tool call format"""
        if "error" in response:
            return response

        choices = response.get("choices", [])
        if not choices:
            return response

        message = choices[0].get("message", {})
        content = message.get("content", "")

        # Try to parse JSON tool call from content
        tool_call = self._parse_json_tool_call(content)

        if tool_call and "tool" in tool_call:
            tool_name = tool_call["tool"]
            arguments = tool_call.get("arguments", {})

            # Convert to standard tool call format
            tool_call_id = f"call_{uuid.uuid4().hex[:24]}"
            message["tool_calls"] = [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments)
                }
            }]
            # Keep the original content for logging
            message["content"] = content

        return response

    def _extract_tool_calls(self, assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from DeepSeek response message"""
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
