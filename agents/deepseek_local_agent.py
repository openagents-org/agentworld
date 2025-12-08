"""
DeepSeek Local Agent for AgentWorld Game
Uses a locally hosted DeepSeek-R1 (Distill Llama-70B) model via vLLM.
Functionality matches the remote DeepSeek agent while avoiding external APIs.
"""

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

from vllm import LLM, SamplingParams

from base_agent import BaseAgent
from deepseek_agent import DeepSeekAgent

# Shared vLLM engine so multiple agents reuse one loaded model
_VLLM_ENGINE = None
_VLLM_TOKENIZER = None
_VLLM_CONFIG: Dict[str, Any] = {}
_VLLM_LOCK = threading.Lock()


class DeepSeekLocalAgent(DeepSeekAgent):
    """Local DeepSeek agent powered by vLLM."""

    def __init__(
        self,
        model: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        dump_prompts: bool = False,
        debug_prints: bool = False,
        tensor_parallel_size: Optional[int] = None,
        gpu_memory_utilization: float = 0.9,
        max_model_len: int = 32768,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9,
        dtype: str = "bfloat16",
    ):
        # Initialize base agent (game + prompts)
        BaseAgent.__init__(self, username, password, base_url, dump_prompts, debug_prints)

        self.provider = "deepseek_local"
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.max_model_len = max_model_len
        self.dtype = dtype
        self.gpu_memory_utilization = gpu_memory_utilization
        self.tensor_parallel_size = tensor_parallel_size or self._auto_tensor_parallel_size()

        # Local pipeline relies on JSON tool instructions for all models
        self.supports_native_tools = False

        self.stop_tokens = ["<|EOT|>", "</s>"]

        # Spin up / reuse shared vLLM engine
        self._init_vllm_engine()

    def _is_r1_model(self, model_name: str) -> bool:
        """Detect if model is an R1 variant (forces JSON tool mode)."""
        normalized = model_name.lower()
        return "deepseek-r1" in normalized or "r1-distill" in normalized

    def _auto_tensor_parallel_size(self) -> int:
        """Pick tensor parallelism from env or GPU count."""
        env_tp = os.getenv("DEEPSEEK_LOCAL_TP_SIZE")
        if env_tp and env_tp.isdigit():
            try:
                return max(1, int(env_tp))
            except Exception:
                pass

        try:
            import torch

            gpu_count = torch.cuda.device_count()
            return max(1, gpu_count)
        except Exception:
            return 1

    def _init_vllm_engine(self):
        """Initialize or reuse a shared vLLM engine."""
        global _VLLM_ENGINE, _VLLM_TOKENIZER, _VLLM_CONFIG

        desired_config = {
            "model": self.model,
            "tensor_parallel_size": self.tensor_parallel_size,
            "gpu_memory_utilization": self.gpu_memory_utilization,
            "max_model_len": self.max_model_len,
            "dtype": self.dtype,
        }

        with _VLLM_LOCK:
            needs_reload = _VLLM_ENGINE is None or any(
                _VLLM_CONFIG.get(k) != v for k, v in desired_config.items()
            )

            if needs_reload:
                _VLLM_ENGINE = LLM(
                    model=self.model,
                    tensor_parallel_size=self.tensor_parallel_size,
                    gpu_memory_utilization=self.gpu_memory_utilization,
                    max_model_len=self.max_model_len,
                    dtype=self.dtype,
                    trust_remote_code=True,
                )
                _VLLM_TOKENIZER = _VLLM_ENGINE.get_tokenizer()
                _VLLM_CONFIG = desired_config

        self.llm = _VLLM_ENGINE
        self.tokenizer = _VLLM_TOKENIZER

    def _normalize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Normalize OpenAI-style messages to simple chat roles for the template."""
        normalized: List[Dict[str, str]] = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content") or ""

            if role == "tool":
                normalized.append(
                    {
                        "role": "user",
                        "content": f"[TOOL RESULT]\n{content}",
                    }
                )
            elif role == "assistant":
                tool_calls = msg.get("tool_calls") or []
                call_summaries = []
                for call in tool_calls:
                    fn = call.get("function", {}).get("name", "")
                    args = call.get("function", {}).get("arguments", "")
                    call_summaries.append(f"{fn}({args})")

                extra = f"\n[PREVIOUS_TOOL_CALLS] {', '.join(call_summaries)}" if call_summaries else ""
                normalized.append({"role": "assistant", "content": f"{content}{extra}".strip()})
            elif role in {"system", "user"}:
                normalized.append({"role": role, "content": content})
            else:
                normalized.append({"role": "user", "content": content})

        return normalized

    def _build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """Render chat messages using the model's chat template."""
        if not self.tokenizer:
            raise RuntimeError("Tokenizer not initialized for vLLM engine")

        normalized_messages = self._normalize_messages(messages)
        return self.tokenizer.apply_chat_template(
            normalized_messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _make_api_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a response with the local vLLM engine."""
        try:
            effective_messages = (
                messages
                if self.supports_native_tools
                else self._inject_json_tool_instructions(messages)
            )

            prompt = self._build_prompt(effective_messages)
            sampling_params = SamplingParams(
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                stop=self.stop_tokens,
            )

            start = time.time()
            with _VLLM_LOCK:
                outputs = self.llm.generate([prompt], sampling_params)
            elapsed = time.time() - start

            if not outputs or not outputs[0].outputs:
                return {"error": "Local DeepSeek generation returned no candidates"}

            content = outputs[0].outputs[0].text
            self._debug_print(f"[vLLM] Generated {len(content)} chars in {elapsed:.2f}s")

            assistant_message: Dict[str, Any] = {"role": "assistant", "content": content}
            response: Dict[str, Any] = {"choices": [{"message": assistant_message}]}

            if not self.supports_native_tools:
                response = self._convert_json_response_to_tool_calls(response)

            return response

        except Exception as e:
            return {"error": f"Local DeepSeek inference failed: {str(e)}"}

