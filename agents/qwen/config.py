"""
Configuration settings for Qwen AI Agent for Kaetram game
"""

import os

# Qwen API Configuration
DASHSCOPE_API_KEY = "sk-961f7e1c3a3e40e2a4b3b407e448c4c1"
QWEN_MODEL = "qwen-plus"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Kaetram Game Server Configuration  
KAETRAM_BASE_URL = "http://localhost:9002"
KAETRAM_API_ENDPOINTS = {
    "create": "/ai/create",
    "login": "/ai/login", 
    "move": "/ai/move",
    "chat": "/ai/chat",
    "observe": "/ai/observe",
    "enter": "/ai/enter",
    "stop": "/ai/stop",
    "equip": "/ai/equip",
    "collect": "/ai/collect",
    "target": "/ai/target",
    "attack": "/ai/attack"
}

# Agent Configuration
AGENT_USERNAME = "QwenAgent"
AGENT_PASSWORD = "qwen123456"
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
OBSERVATION_RADIUS = 64

# Game Strategy Configuration
EXPLORATION_PRIORITY = True
RESOURCE_COLLECTION = True
COMBAT_ENABLED = True
CHAT_ENABLED = True 