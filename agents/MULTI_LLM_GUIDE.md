# Multi-LLM Agent Console Guide

The enhanced AgentWorld console now supports multiple LLM providers, allowing you to choose between different AI models to control your game agent.

## Supported LLM Providers

| Provider | Description | Default Model | API Key Required |
|----------|-------------|---------------|------------------|
| **qwen** | Alibaba Cloud Qwen (DashScope) | qwen-plus | No (uses config) |
| **openai** | OpenAI (GPT-4, GPT-3.5, etc.) | gpt-4o | Yes |
| **claude** | Anthropic Claude | claude-3-5-sonnet-20241022 | Yes |
| **deepseek** | DeepSeek | deepseek-chat | Yes |

## Quick Start Examples

### 1. Using Qwen (Default)
```bash
# Uses existing Qwen configuration
python console.py

# Interactive mode with Qwen
python console.py --provider qwen
```

### 2. Using OpenAI GPT-4
```bash
# With command-line API key
python console.py --provider openai --api-key sk-your-openai-key

# Using environment variable
export OPENAI_API_KEY=sk-your-openai-key
python console.py --provider openai

# Specify a different OpenAI model
python console.py --provider openai --api-key sk-... --model gpt-3.5-turbo
```

### 3. Using Anthropic Claude
```bash
# With command-line API key
python console.py --provider claude --api-key sk-ant-your-claude-key

# Using environment variable
export ANTHROPIC_API_KEY=sk-ant-your-claude-key
python console.py --provider claude

# Specify a different Claude model
python console.py --provider claude --api-key sk-ant-... --model claude-3-haiku-20240307
```

### 4. Using DeepSeek
```bash
# With command-line API key
python console.py --provider deepseek --api-key sk-your-deepseek-key

# Using environment variable
export DEEPSEEK_API_KEY=sk-your-deepseek-key
python console.py --provider deepseek
```

### 5. Single Task Mode
```bash
# Run a single task with different providers
python console.py --provider openai --api-key sk-... --task "Explore the forest and collect resources"
python console.py --provider claude --api-key sk-... --task "Fight enemies until level 5"
python console.py --provider deepseek --api-key sk-... --task "Find and equip better weapons"
```

## Environment Variables

Set these environment variables to avoid passing API keys via command line:

```bash
# OpenAI
export OPENAI_API_KEY=sk-your-openai-key

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-your-claude-key

# DeepSeek
export DEEPSEEK_API_KEY=sk-your-deepseek-key

# Default provider (optional)
export DEFAULT_LLM_PROVIDER=openai  # or claude, deepseek, qwen
```

## Configuration File

You can also edit `config.py` to set default values:

```python
# Default LLM Provider
DEFAULT_LLM_PROVIDER = "openai"  # Change this to your preferred provider

# API Keys (not recommended for production)
OPENAI_API_KEY = "sk-your-key-here"
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
DEEPSEEK_API_KEY = "sk-your-key-here"
```

## Command Line Options

```bash
python console.py [OPTIONS]

Options:
  --provider {qwen,openai,claude,deepseek}
                        LLM provider to use (default: qwen)
  --api-key API_KEY     API key for the LLM provider
  --model MODEL         Model name to use (optional)
  --username USERNAME   Game username (default: from config)
  --password PASSWORD   Game password (default: from config)
  --task TASK          Execute a single task and exit
  --max-iterations N   Maximum iterations per task (default: 50)
```

## Available Models

### OpenAI Models
- `gpt-4o` (default)
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### Claude Models
- `claude-3-5-sonnet-20241022` (default)
- `claude-3-5-haiku-20241022`
- `claude-3-opus-20240229`

### DeepSeek Models
- `deepseek-chat` (default)
- `deepseek-coder`

### Qwen Models
- `qwen-plus` (default)
- `qwen-turbo`
- `qwen-max`

## Interactive Console Features

All LLM providers support the same interactive features:

- **Natural language commands**: "explore the area", "fight monsters", "collect resources"
- **Cheat commands**: `/teleport`, `/equip`, `/setlevel`, `/fullequip`
- **Session management**: `reset`, `stats`, `save`, `history`, `logout`, `exit`
- **Auto-login**: Automatic game login without LLM prompting
- **Real-time status**: Player stats displayed above each prompt

## Provider-Specific Notes

### Qwen (Alibaba Cloud)
- Uses existing DashScope configuration
- No additional API key required
- Optimized for Chinese and English

### OpenAI
- Requires OpenAI API key
- Excellent function calling support
- Good for general-purpose tasks

### Anthropic Claude
- Requires Anthropic API key
- Strong reasoning capabilities
- Good for complex strategic decisions

### DeepSeek
- Requires DeepSeek API key
- Good performance with technical tasks
- Cost-effective option

## Troubleshooting

### API Key Issues
```bash
❌ Error: API key required for openai provider.
   Please provide --api-key argument or set environment variable.
   Set OPENAI_API_KEY environment variable
```
**Solution**: Provide API key via `--api-key` argument or set environment variable.

### Provider Not Supported
```bash
❌ Failed to create agent: Unsupported provider: gpt. Supported providers: qwen, openai, claude, deepseek
```
**Solution**: Use one of the supported provider names: `qwen`, `openai`, `claude`, `deepseek`.

### Model Not Available
```bash
❌ API call failed: 404 Client Error
```
**Solution**: Check if the specified model is available for your provider and API key.

## Best Practices

1. **Use environment variables** for API keys instead of command-line arguments
2. **Start with default models** before trying alternative models
3. **Test connectivity** with a simple task before complex operations
4. **Monitor API usage** and costs when using paid providers
5. **Use Qwen** for testing and development (no external API costs)

## Advanced Usage

### Custom Agent Classes
You can extend the system by creating new agent classes that inherit from `BaseAgent`:

```python
from base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def _make_api_call(self, messages):
        # Your custom LLM API implementation
        pass
    
    def _extract_tool_calls(self, assistant_message):
        # Your custom tool call extraction
        pass
```

### Adding to Agent Factory
Register your custom agent in `agent_factory.py`:

```python
# In AgentFactory.create_agent()
elif provider == "mycustom":
    return MyCustomAgent(api_key=api_key, model=model, username=username, password=password)
```

Then use it with the console:

```bash
python console.py --provider mycustom --api-key your-key
```

## Support

For issues or questions:
1. Check this guide for common solutions
2. Verify API keys and provider configurations
3. Test with Qwen provider to isolate LLM-specific issues
4. Check game server connectivity (`http://localhost:9002`)