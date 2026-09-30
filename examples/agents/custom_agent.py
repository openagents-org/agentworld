"""Runnable adapter example: retains the reference OpenAI-compatible policy.

Replace _make_api_call and _extract_tool_calls for another model protocol.
Keep BaseAgent's one-action-per-turn execution and trajectory recording contract.
"""
from openai_agent import OpenAIAgent


class CustomAgent(OpenAIAgent):
    def __init__(self, *, api_key, model, username, password, base_url,
                 dump_prompts, llm_params):
        super().__init__(api_key=api_key, model=model, username=username,
                         password=password, base_url=base_url,
                         dump_prompts=dump_prompts, llm_params=llm_params)
