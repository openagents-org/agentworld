"""
Agent Factory for Creating Different LLM Agents
Provides a unified interface to create agents for different LLM providers
"""

from typing import Optional
from base_agent import BaseAgent
from qwen_agent import QwenAgent
from openai_agent import OpenAIAgent
from claude_agent import ClaudeAgent
from deepseek_agent import DeepSeekAgent


class AgentFactory:
    """Factory class for creating different types of LLM agents"""
    
    SUPPORTED_PROVIDERS = {
        "qwen": "Alibaba Cloud Qwen (DashScope)",
        "openai": "OpenAI (GPT-4, GPT-3.5, etc.)",
        "claude": "Anthropic Claude",
        "deepseek": "DeepSeek"
    }
    
    @classmethod
    def create_agent(
        cls,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> BaseAgent:
        """
        Create an agent based on the specified provider
        
        Args:
            provider: The LLM provider ('qwen', 'openai', 'claude', 'deepseek')
            api_key: API key for the provider (required for non-Qwen providers)
            model: Model name to use (optional, uses defaults if not specified)
            username: Game username (optional)
            password: Game password (optional)
            
        Returns:
            BaseAgent: An instance of the appropriate agent class
            
        Raises:
            ValueError: If provider is not supported or required parameters are missing
        """
        provider = provider.lower().strip()
        
        if provider not in cls.SUPPORTED_PROVIDERS:
            supported = ", ".join(cls.SUPPORTED_PROVIDERS.keys())
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {supported}")
        
        if provider == "qwen":
            return QwenAgent(username=username, password=password)
        
        elif provider == "openai":
            if not api_key:
                raise ValueError("OpenAI API key is required for OpenAI provider")
            default_model = model or "gpt-4o"
            return OpenAIAgent(api_key=api_key, model=default_model, username=username, password=password)
        
        elif provider == "claude":
            if not api_key:
                raise ValueError("Anthropic API key is required for Claude provider")
            default_model = model or "claude-3-5-sonnet-20241022"
            return ClaudeAgent(api_key=api_key, model=default_model, username=username, password=password)
        
        elif provider == "deepseek":
            if not api_key:
                raise ValueError("DeepSeek API key is required for DeepSeek provider")
            default_model = model or "deepseek-chat"
            return DeepSeekAgent(api_key=api_key, model=default_model, username=username, password=password)
        
        else:
            # This should never happen due to the earlier check
            raise ValueError(f"Provider implementation not found: {provider}")
    
    @classmethod
    def list_supported_providers(cls) -> dict:
        """Return a dictionary of supported providers and their descriptions"""
        return cls.SUPPORTED_PROVIDERS.copy()
    
    @classmethod
    def get_default_models(cls) -> dict:
        """Return default models for each provider"""
        return {
            "qwen": "qwen-plus",
            "openai": "gpt-4o",
            "claude": "claude-3-5-sonnet-20241022",
            "deepseek": "deepseek-chat"
        }
    
    @classmethod
    def validate_provider_config(cls, provider: str, api_key: Optional[str] = None) -> bool:
        """
        Validate if the provider configuration is valid
        
        Args:
            provider: The LLM provider name
            api_key: API key for the provider
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        provider = provider.lower().strip()
        
        if provider not in cls.SUPPORTED_PROVIDERS:
            return False
        
        # Qwen doesn't need external API key validation (uses config)
        if provider == "qwen":
            return True
        
        # All other providers require API keys
        return api_key is not None and api_key.strip() != ""