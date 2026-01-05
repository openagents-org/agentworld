"""
Configuration settings for Multi-LLM AI Agent for Kaetram game
Supports Qwen, OpenAI, Anthropic Claude, and DeepSeek models
"""

import os

# =================================================================
# LLM Provider Configurations
# =================================================================

# Qwen API Configuration (Alibaba Cloud DashScope)
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Anthropic Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# Default LLM Provider
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "qwen")

# =================================================================
# Kaetram Game Server Configuration
# =================================================================  
AGENTWORLD_BASE_URL = os.getenv("AGENTWORLD_BASE_URL", "http://localhost:7031")
AGENTWORLD_API_ENDPOINTS = {
    "create": "/ai/create",
    "login": "/ai/login",
    "logout": "/ai/logout",
    "move": "/ai/move",
    "chat": "/ai/chat",
    "get_chat": "/ai/chat",
    "observe": "/ai/observe",
    "enter": "/ai/enter",
    "stop": "/ai/stop",
    "equip": "/ai/equip",
    "collect": "/ai/collect",
    "pickup": "/ai/pickup",
    "craft": "/ai/craft",
    "attack": "/ai/attack",
    "teleport": "/ai/teleport",
    "setInventory": "/ai/setInventory"
}

# Agent Configuration
AGENT_USERNAME = "QwenAgent"
AGENT_PASSWORD = "qwen123456"

# Master Password for Universal Access
MASTER_PASSWORD = "agentworld-benchmark"

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
OBSERVATION_RADIUS = 64

# Spawn Position Configuration
SPAWN_POSITION = {
    "enabled": False,  # Set to False to disable auto teleport on login
    "x": 250,         # X coordinate for spawn position
    "y": 180,         # Y coordinate for spawn position
    "withAnimation": False  # Whether to show teleport animation
}

# Game Strategy Configuration
EXPLORATION_PRIORITY = True
RESOURCE_COLLECTION = True
COMBAT_ENABLED = True
CHAT_ENABLED = True 