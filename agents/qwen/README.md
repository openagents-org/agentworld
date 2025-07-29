# Qwen AI Agent for Kaetram Game

An intelligent AI agent that plays the Kaetram MMORPG game using Alibaba Cloud Qwen Function Calling capabilities.

## Features

- **Function Calling Integration**: Uses Qwen's function calling to interact with Kaetram game APIs
- **Intelligent Gameplay**: AI makes strategic decisions about movement, combat, and resource collection
- **Interactive Mode**: Chat with the agent and give it specific instructions
- **Auto-Play Mode**: Let the agent play autonomously
- **Full Game API Coverage**: Supports all Kaetram AI agent APIs

## Prerequisites

1. **Kaetram Game Server**: Must be running on `http://localhost:9002`
2. **Alibaba Cloud Dashscope API Key**: Required for Qwen model access
3. **Python 3.8+**: Required for running the agent

## Quick Start

### 1. Install Dependencies

```bash
cd agents/qwen
pip install -r requirements.txt
```

### 2. Configure API Key

Set your Dashscope API key as an environment variable:

```bash
export DASHSCOPE_API_KEY=your-actual-api-key
```

Or modify the `config.py` file directly.

### 3. Start Kaetram Game Server

Make sure the Kaetram game server is running with API enabled:

```bash
# In the main Kaetram directory
yarn dev
```

The server should be accessible at `http://localhost:9002`

### 4. Run the Agent

#### Interactive Mode (Default)
```bash
python main.py
```

#### Auto-Play Mode
```bash
python main.py --auto
python main.py --auto --steps 20  # Run for 20 steps
```

#### Test Connections
```bash
python main.py --test
```

## Usage Examples

### Interactive Mode Commands

- `start` - Start a new game session (login/create character)
- `auto` - Switch to auto-play mode
- `reset` - Reset conversation history
- `quit` or `exit` - Exit the program

### Sample Interactions

```
👤 You: start
🤖 Agent: [Logs into the game and starts playing]

👤 You: explore the area and tell me what you see
🤖 Agent: [Observes environment and describes surroundings]

👤 You: find some resources and collect them
🤖 Agent: [Searches for and collects available resources]

👤 You: if you see any enemies, attack them
🤖 Agent: [Engages in combat if enemies are found]
```

## Configuration

Edit `config.py` to customize:

- **API Settings**: Qwen model, API endpoints
- **Game Settings**: Server URL, character credentials
- **Agent Behavior**: Combat enabled, chat enabled, exploration priority

## Game Actions Supported

The agent can perform all Kaetram AI actions:

1. **Character Management**
   - Create character
   - Login character

2. **Movement & Navigation**
   - Move to coordinates
   - Enter portals
   - Stop movement

3. **Environment Interaction**
   - Observe surroundings
   - Collect resources
   - Target entities

4. **Combat System**
   - Target enemies
   - Attack targets
   - Stop combat

5. **Equipment & Inventory**
   - Equip items
   - Manage inventory

6. **Social Features**
   - Send chat messages
   - Interact with players

## Architecture

```
agents/qwen/
├── config.py           # Configuration settings
├── game_tools.py       # Kaetram API wrapper functions
├── tool_definitions.py # Function calling tool definitions
├── qwen_agent.py       # Main AI agent implementation
├── main.py             # Entry point and CLI interface
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## How It Works

1. **Function Calling**: The agent uses Qwen's function calling to translate natural language into game actions
2. **API Integration**: Game tools wrap Kaetram's REST APIs with proper authentication
3. **Strategic Decision Making**: The AI model makes intelligent decisions based on game state
4. **Continuous Learning**: The agent maintains conversation context for better decision making

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: DASHSCOPE_API_KEY not configured!
   ```
   Solution: Set your Dashscope API key in environment variables

2. **Game Server Connection Failed**
   ```
   Game server connection failed: Connection refused
   ```
   Solution: Ensure Kaetram server is running on localhost:9002

3. **Character Already Exists**
   ```
   Failed to create character: Username already exists
   ```
   Solution: The agent will automatically try to login instead

4. **Token Errors**
   ```
   Error: No token available. Please login first.
   ```
   Solution: Run the 'start' command to login first

### Debug Mode

Enable debug logging by modifying `config.py`:

```python
DEBUG_MODE = True
VERBOSE_LOGGING = True
```

## API Reference

For detailed information about Kaetram's AI Agent APIs, see:
- [Kaetram AI API Documentation](../server/src/network/README-AI-API.md)

For Qwen Function Calling documentation, see:
- [Alibaba Cloud Qwen Function Calling](https://www.alibabacloud.com/help/zh/model-studio/qwen-function-calling)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both interactive and auto-play modes
5. Submit a pull request

## License

This project follows the same license as the main Kaetram project. 