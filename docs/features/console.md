# AgentWorld Console Guide

The AgentWorld Console is a powerful command-line interface that allows you to control AI agents in the game using natural language commands or direct cheat commands. It supports multiple LLM providers and offers extensive configuration options for setting up agents with specific initial states.

## Table of Contents

- [Quick Start](#quick-start)
- [LLM Providers](#llm-providers)
- [Usage Modes](#usage-modes)
- [Initial State Configuration](#initial-state-configuration)
- [Cheat Commands](#cheat-commands)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

```bash
# Start interactive console with default provider (Qwen)
python agents/console.py --username mybot --password mypass

# Use OpenAI GPT-4
python agents/console.py --provider openai --api-key sk-... --username mybot --password mypass

# Single task execution
python agents/console.py --task "explore the area" --username mybot --password mypass
```

### Prerequisites

1. **Game Server**: Ensure the AgentWorld server is running
2. **API Keys**: Set up API keys for your chosen LLM provider
3. **Python Environment**: Python 3.8+ with required dependencies

## LLM Providers

The console supports multiple AI providers:

### Qwen (Default)
```bash
export DASHSCOPE_API_KEY="your-key"
python agents/console.py --provider qwen --model qwen-plus
```

### OpenAI
```bash
export OPENAI_API_KEY="your-key"
python agents/console.py --provider openai --model gpt-4o
```

### Anthropic Claude
```bash
export ANTHROPIC_API_KEY="your-key"
python agents/console.py --provider claude --model claude-3-5-sonnet-20241022
```

### DeepSeek
```bash
export DEEPSEEK_API_KEY="your-key"
python agents/console.py --provider deepseek --model deepseek-chat
```

## Usage Modes

### Interactive Mode

In interactive mode, you can chat with the agent and give it instructions:

```bash
python agents/console.py --username mybot --password mypass
```

**Interactive Commands:**
- Natural language: `"explore the forest"`, `"fight nearby enemies"`
- `reset` - Reset conversation and re-login
- `stats` - Show session statistics
- `save` - Save session logs
- `history` - Show conversation history
- `logout` - Logout current session
- `exit` - Quit the console

### Single Task Mode

Execute a single task and exit:

```bash
python agents/console.py --task "collect resources and fight mobs" --username mybot --password mypass
```

### Cheat Command Mode

Execute cheat commands directly:

```bash
python agents/console.py --task "/observe 32" --username mybot --password mypass
python agents/console.py --task "/teleport 300 200" --username mybot --password mypass
```

## Initial State Configuration

Set up your agent's starting state with command-line options:

### Location Setting

Teleport to specific coordinates at startup:

```bash
--location x,y

# Examples
--location 250,180    # Spawn point
--location 300,200    # Custom location
```

### Combat Levels

Set individual combat skill levels (1-120):

```bash
--combat-level-accuracy 45
--combat-level-strength 50
--combat-level-defense 40
--combat-level-health 60
--combat-level-magic 35
--combat-level-archery 30
```

**Note:** HP and MP are automatically restored to maximum after setting combat levels.

### Equipment Setup

Equip items at startup:

```bash
--equipped-items item1 item2:count:enchant

# Examples
--equipped-items coppersword ironhelmet
--equipped-items bastardsword:1:2 whitearmor goldboots:1:3
```

### Inventory Items

Add items to inventory at startup:

```bash
--inventory-items item1:count item2:count:enchant

# Examples
--inventory-items stick:20 bead:10
--inventory-items healingpotion:15 firepotion:10 pythararrow:100:2
```

### New Character Creation

Create fresh characters or reset existing ones:

```bash
--new-character

# Features:
# - No password required
# - Auto-creates if username doesn't exist
# - Resets to default state if character exists
# - Works with all other initial state options
```

## Cheat Commands

Cheat commands work in both interactive mode and with `--task`:

### Environment Observation
```bash
/observe [radius]

# Examples
/observe          # Default radius (64)
/observe 32       # Custom radius
/observe 150      # Large area scan
```

### Teleportation
```bash
/teleport x y [withAnimation]
/teleport spawn

# Examples
/teleport 300 200           # Teleport to coordinates
/teleport 250 180 true      # With animation
/teleport spawn             # Go to spawn point
```

### Equipment Management
```bash
/equip <item> [count] [enchant]
/fullequip

# Examples
/equip coppersword                # Basic equipment
/equip ironhelmet 1 3            # With +3 enchantment
/fullequip                       # Complete equipment set
```

### Item Management
```bash
/give <item> [count]

# Examples
/give stick 10              # Give 10 sticks
/give healingpotion 5       # Give 5 healing potions
/give ironbar 20            # Give crafting materials
```

### Level Management
```bash
/setlevel <level>

# Examples
/setlevel 45                # Set all combat skills to 45
/setlevel 120               # Maximum level
```

## Advanced Features

### Session Logging

Save all interactions to a file:

```bash
--output session.log

# Logs include:
# - All user inputs and agent responses
# - Tool calls and results
# - System messages and errors
# - Session statistics and conversation history
```

### Multiple Initial State Options

Combine multiple configuration options:

```bash
python agents/console.py \
  --provider openai \
  --username combatbot \
  --new-character \
  --location 400,300 \
  --combat-level-accuracy 70 \
  --combat-level-strength 75 \
  --combat-level-defense 60 \
  --equipped-items bastardsword:1:3 whitearmor goldboots \
  --inventory-items healingpotion:20 firepotion:15 pythararrow:200 \
  --task "/observe 64"
```

### Custom Server Connection

Connect to different game servers:

```bash
--host http://localhost:9001
--host https://your-server.com:7032
```

## Examples

### Research and Testing

```bash
# Quick environment scan
python agents/console.py --username scanner --new-character --task "/observe 100"

# Test combat setup
python agents/console.py \
  --username fighter \
  --new-character \
  --combat-level-strength 80 \
  --equipped-items bastardsword whitearmor \
  --inventory-items healingpotion:50 \
  --task "find and fight strong enemies"

# Resource gathering bot
python agents/console.py \
  --username gatherer \
  --new-character \
  --location 200,150 \
  --equipped-items ironaxe ironpickaxe \
  --task "collect wood and ore for 10 minutes"
```

### Interactive Development

```bash
# Development session with logging
python agents/console.py \
  --provider openai \
  --username devbot \
  --password dev123 \
  --location 250,180 \
  --output development.log

# Then in interactive mode:
🎮 What would you like to do? > explore the northern forest
🎮 What would you like to do? > /observe 50
🎮 What would you like to do? > attack any wolves you see
```

### Performance Testing

```bash
# High-level combat test
python agents/console.py \
  --username testbot \
  --new-character \
  --combat-level-accuracy 90 \
  --combat-level-strength 95 \
  --combat-level-defense 85 \
  --equipped-items dragonsword:1:5 dragonarmor:1:4 \
  --inventory-items superpotion:100 \
  --location 500,400 \
  --task "engage in combat with the strongest enemies for testing"
```

## Troubleshooting

### Common Issues

**Login Failures:**
```bash
# Try with --new-character to bypass password issues
python agents/console.py --new-character --username mybot --task "/observe"
```

**API Key Issues:**
```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Or use command line
python agents/console.py --provider openai --api-key sk-...
```

**Connection Issues:**
```bash
# Check server URL
python agents/console.py --host http://localhost:7032

# Test with simple command
python agents/console.py --task "/observe" --username test --new-character
```

**Character State Issues:**
```bash
# Reset character to fresh state
python agents/console.py --new-character --username mybot --task "/observe"

# Clear and set specific state
python agents/console.py \
  --new-character \
  --username mybot \
  --location 250,180 \
  --combat-level-accuracy 1 \
  --task "start fresh adventure"
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Save detailed logs
python agents/console.py \
  --username debugbot \
  --new-character \
  --output debug.log \
  --task "/observe"

# Check the log file for detailed information
cat debug.log
```

### Server Configuration

Ensure your server configuration allows AI agents:

```bash
# Check if AI endpoints are accessible
curl http://localhost:7032/ai/create -X POST -H "Content-Type: application/json" -d '{"username":"test","password":"test"}'
```

## Tips and Best Practices

1. **Use --new-character** for fresh testing sessions
2. **Set up environment variables** for API keys rather than using --api-key
3. **Save logs** with --output for debugging and analysis
4. **Start with simple commands** like `/observe` to test connectivity
5. **Use specific coordinates** with --location for consistent testing
6. **Combine initial state options** to set up complex scenarios quickly
7. **Test cheat commands** in task mode for automated workflows

## Command Reference

### Required Parameters
- `--username` - Character username
- Either `--password` or `--new-character`

### Optional Parameters
- `--provider` - LLM provider (qwen, openai, claude, deepseek)
- `--api-key` - API key (if not set via environment)
- `--model` - Specific model name
- `--host` - Game server URL
- `--task` - Single task to execute
- `--output` - Log file path
- `--max-iterations` - Maximum iterations per task

### Initial State Parameters
- `--location x,y` - Starting coordinates
- `--combat-level-{skill} N` - Set skill levels
- `--equipped-items` - Starting equipment
- `--inventory-items` - Starting inventory
- `--new-character` - Create/reset character

### Interactive Commands
- Natural language instructions
- `/observe [radius]` - Environment scan
- `/teleport x y` - Move to location
- `/equip item [count] [enchant]` - Equip items
- `/give item [count]` - Add items
- `/setlevel level` - Set combat level
- `/fullequip` - Complete equipment set
- `reset`, `stats`, `save`, `history`, `logout`, `exit`

This console provides a powerful interface for AI agent development, testing, and research in the AgentWorld environment.
