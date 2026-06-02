#!/usr/bin/env python3
"""
AgentWorld Task Runner

A comprehensive task runner that executes tasks from YAML configuration files using
specified agent configurations. Supports running single tasks or entire folders of tasks.

Usage:
    python run.py --task path/to/task.yaml --agent path/to/agent.yaml --output logs/
    python run.py --task-folder data_v0.1_solo/ --agent configs/qwen_agent.yaml --output logs/
"""

import argparse
import os
import sys
import yaml
import json
import time
import logging
import signal
import atexit
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from jinja2 import Template, Environment, meta
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

# Import existing agent components
from agent_factory import AgentFactory
from console import GameConsole
from config import MASTER_PASSWORD
from base_agent import BaseAgent
from experiment import ExperimentConfig, RandomAgentPolicy, DEFAULT_MAX_ROUNDS


class ConfigurableAgent:
    """Wrapper for BaseAgent that allows custom system prompt configuration"""
    
    def __init__(self, base_agent: BaseAgent, custom_system_prompt: Optional[str] = None):
        self.base_agent = base_agent
        self.custom_system_prompt = custom_system_prompt
        
        # Override the system prompt if provided
        if self.custom_system_prompt:
            self._override_system_prompt()
    
    def _override_system_prompt(self):
        """Override the base agent's system prompt building method"""
        original_build_method = self.base_agent._build_system_prompt
        
        def custom_build_system_prompt():
            # Use custom system prompt template with Jinja2 rendering
            base_prompt = self.custom_system_prompt
            
            # Get current environment observation and chat messages for the system prompt
            current_observation = self.base_agent._get_current_environment_observation()
            chat_messages = self.base_agent._get_current_chat_messages()
            
            # Try to use Jinja2 template rendering
            try:
                template = Template(base_prompt)
                template_vars = {
                    'observation': current_observation or "No observation data available",
                    'chat_messages': chat_messages or "No chat messages in current session"
                }
                return template.render(**template_vars)
            except Exception:
                # Fallback to simple string replacement for backward compatibility
                if "{{observation}}" in base_prompt:
                    base_prompt = base_prompt.replace("{{observation}}", current_observation or "No observation data available")
                else:
                    # Fallback: append observation if placeholder not found
                    if current_observation:
                        base_prompt += f"\n\n=== CURRENT ENVIRONMENT OBSERVATION ===\n{current_observation}\n=== END OBSERVATION ==="
                
                if "{{chat_messages}}" in base_prompt:
                    base_prompt = base_prompt.replace("{{chat_messages}}", chat_messages or "No chat messages in current session")
                else:
                    # Fallback: append chat messages if placeholder not found
                    if chat_messages:
                        base_prompt += f"\n\n=== CHAT HISTORY ===\n{chat_messages}\n=== END CHAT HISTORY ==="
                
                return base_prompt
        
        # Replace the method
        self.base_agent._build_system_prompt = custom_build_system_prompt
    
    def __getattr__(self, name):
        """Delegate all other attributes to the base agent"""
        return getattr(self.base_agent, name)


@dataclass
class TaskConfig:
    """Task configuration data structure"""
    name: str
    description: str
    objectives: Dict[str, Any]
    max_action_steps: int
    agents: Dict[str, Dict[str, Any]]
    success_criteria: List[str]
    relevant_game_context: Optional[str] = None
    rounds: Optional[int] = None
    shared_plan: Optional[str] = None


@dataclass
class AgentConfig:
    """Agent configuration data structure"""
    name: str
    provider: str
    llm: Dict[str, Any]
    game: Dict[str, Any]
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None


class AgentState(Enum):
    """Agent execution states"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentExecutionState:
    """Tracks the execution state of an agent during multi-agent tasks"""
    agent_name: str
    console: GameConsole
    state: AgentState
    action_count: int
    chat_count: int
    last_response: str
    completion_reason: Optional[str] = None
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class SplitScreenDisplay:
    """Manages split-screen terminal display with agent logs and chat room"""
    
    def __init__(self):
        self.stdscr = None
        self.log_win = None
        self.chat_win = None
        self.log_queue = queue.Queue()
        self.chat_queue = queue.Queue()
        self.chat_messages = []
        self.log_lines = []
        self.max_chat_messages = 100
        self.max_log_lines = 1000
        self.running = True
        
    def init_curses(self):
        """Initialize curses interface"""
        if not CURSES_AVAILABLE:
            return False
            
        try:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.nodelay(1)
            curses.start_color()
            
            # Initialize color pairs
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Success
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Info
            curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Chat
            curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Agent
            
            self.setup_windows()
            return True
        except Exception:
            return False
    
    def setup_windows(self):
        """Setup split-screen windows"""
        height, width = self.stdscr.getmaxyx()
        
        # Split screen vertically (60/40 - more space for logs)
        split_col = int(width * 0.6)
        
        # Create bordered windows
        self.log_win = curses.newwin(height - 2, split_col - 1, 1, 0)
        self.chat_win = curses.newwin(height - 2, width - split_col, 1, split_col)
        
        # Add borders and titles
        self.stdscr.addstr(0, 2, "🤖 AGENT LOGS", curses.color_pair(6) | curses.A_BOLD)
        self.stdscr.addstr(0, split_col + 2, "💬 CHAT ROOM", curses.color_pair(5) | curses.A_BOLD)
        
        # Draw vertical separator
        for i in range(1, height - 1):
            try:
                self.stdscr.addstr(i, split_col - 1, "│")
            except curses.error:
                pass
        
        self.stdscr.refresh()
        
    def add_log(self, message: str, color_pair: int = 0):
        """Add a log message to the left panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.log_queue.put((formatted_msg, color_pair))
        
    def add_chat(self, agent_name: str, message: str, username: str = ""):
        """Add a chat message to the right panel"""
        # Format: [agent X | username]: message
        if username:
            formatted_msg = f"[{agent_name} | {username}]: {message}"
        else:
            formatted_msg = f"[{agent_name}]: {message}"
        
        self.chat_queue.put(formatted_msg)
        # Add empty line after each message for better readability
        self.chat_queue.put("")
        
    def update_display(self):
        """Update both panels with new messages"""
        if not self.stdscr:
            return
            
        try:
            # Process log messages
            while not self.log_queue.empty():
                try:
                    msg, color = self.log_queue.get_nowait()
                    self.log_lines.append((msg, color))
                    if len(self.log_lines) > self.max_log_lines:
                        self.log_lines.pop(0)
                except queue.Empty:
                    break
            
            # Process chat messages
            while not self.chat_queue.empty():
                try:
                    msg = self.chat_queue.get_nowait()
                    self.chat_messages.append(msg)
                    if len(self.chat_messages) > self.max_chat_messages:
                        self.chat_messages.pop(0)
                except queue.Empty:
                    break
            
            # Update log window
            self.log_win.clear()
            height, width = self.log_win.getmaxyx()
            
            # Show recent log lines
            start_idx = max(0, len(self.log_lines) - height)
            for i, (line, color) in enumerate(self.log_lines[start_idx:]):
                if i >= height:
                    break
                try:
                    # Truncate line if too long
                    display_line = line[:width-2] if len(line) > width-2 else line
                    if color:
                        self.log_win.addstr(i, 0, display_line, curses.color_pair(color))
                    else:
                        self.log_win.addstr(i, 0, display_line)
                except curses.error:
                    pass
            
            self.log_win.refresh()
            
            # Update chat window
            self.chat_win.clear()
            height, width = self.chat_win.getmaxyx()
            
            # Prepare wrapped chat messages
            wrapped_lines = []
            max_width = max(10, width - 2)  # Ensure minimum width of 10 chars
            
            for msg in self.chat_messages:
                # Handle empty messages
                if not msg.strip():
                    wrapped_lines.append("")
                    continue
                
                # Word wrap the message
                if len(msg) <= max_width:
                    wrapped_lines.append(msg)
                else:
                    # Split message into words and wrap intelligently
                    words = msg.split(' ')
                    current_line = ""
                    
                    for word in words:
                        # Check if adding this word would exceed width
                        test_line = current_line + (" " if current_line else "") + word
                        
                        if len(test_line) <= max_width:
                            current_line = test_line
                        else:
                            # Current line is full, save it and start new line
                            if current_line:
                                wrapped_lines.append(current_line)
                            
                            # Handle very long words that need to be broken
                            if len(word) > max_width:
                                while len(word) > max_width:
                                    wrapped_lines.append(word[:max_width])
                                    word = word[max_width:]
                                current_line = word if word else ""
                            else:
                                current_line = word
                    
                    # Add any remaining content
                    if current_line:
                        wrapped_lines.append(current_line)
            
            # Show recent wrapped lines (from bottom up)
            start_idx = max(0, len(wrapped_lines) - height)
            for i, line in enumerate(wrapped_lines[start_idx:]):
                if i >= height:
                    break
                try:
                    self.chat_win.addstr(i, 0, line, curses.color_pair(5))
                except curses.error:
                    pass
            
            self.chat_win.refresh()
            
        except Exception as e:
            # Fallback to regular print if curses fails
            pass
    
    def cleanup(self):
        """Clean up curses interface"""
        self.running = False
        if self.stdscr:
            try:
                curses.nocbreak()
                self.stdscr.keypad(False)
                curses.echo()
                curses.endwin()
            except:
                pass


class TaskRunner:
    """Main task runner class"""
    
    def __init__(self, agent_config_path: str, output_dir: str, use_split_screen: bool = True, dump_prompts: bool = False, experiment: Optional[ExperimentConfig] = None):
        """Initialize the task runner"""
        self.agent_config_path = agent_config_path
        self.dump_prompts = dump_prompts
        self.experiment = experiment or ExperimentConfig()
        
        # Create a unique run folder for this execution
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_output_dir = Path(output_dir)
        # Direct output to the specified directory without run_timestamp subfolder
        self.output_dir = self.base_output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load agent configuration
        self.agent_config = self._load_agent_config()
        
        # Split-screen display
        self.use_split_screen = use_split_screen and CURSES_AVAILABLE
        self.display = None
        if self.use_split_screen:
            self.display = SplitScreenDisplay()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize agent states tracking for cleanup
        self.active_agent_states: Dict[str, AgentExecutionState] = {}
        self.cleanup_registered = False
        
        self.logger.info(f"TaskRunner initialized with agent config: {agent_config_path}")
        self.logger.info(f"Run folder created: {self.output_dir}")
        self.logger.info(f"Run timestamp: {self.run_timestamp}")
        
        # Set global logger for game tools detailed error reporting
        from game_tools import KaetramGameTools
        KaetramGameTools.set_global_logger(self.logger)
        
        # Log the error log file path for reference
        self.logger.info(f"📝 API errors will be logged to: {self.error_log_file}")
        
        # Initialize split-screen display if available
        if self.use_split_screen and self.display:
            if self.display.init_curses():
                self.log_message("TaskRunner initialized with split-screen display", color=4)
            else:
                self.use_split_screen = False
                self.display = None
                self.logger.warning("Failed to initialize split-screen display, falling back to regular output")
        
        # Initialize trajectory tracking
        self.trajectory_data = {
            'task_id': None,
            'timestamp': None,
            'task_definition': None,
            'rounds': [],
            'metrics': {}
        }
    
    def _load_agent_config(self) -> AgentConfig:
        """Load agent configuration from YAML file"""
        try:
            with open(self.agent_config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            agent_data = config_data['agent']
            return AgentConfig(
                name=agent_data['name'],
                provider=agent_data['provider'],
                llm=agent_data['llm'],
                game=agent_data['game'],
                system_prompt=agent_data.get('system_prompt'),
                user_prompt_template=agent_data.get('user_prompt_template')
            )
        except Exception as e:
            print(f"❌ Error loading agent config from {self.agent_config_path}: {e}")
            sys.exit(1)
    
    def _load_task_config(self, task_path: str) -> TaskConfig:
        """Load task configuration from YAML file"""
        try:
            with open(task_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Extract agents (looking for agent_1, agent_2, etc.)
            agents = {}
            for key, value in config_data.items():
                if key.startswith('agent_'):
                    agents[key] = value
            
            return TaskConfig(
                name=config_data['task']['name'],
                description=config_data['task']['description'],
                objectives=config_data['objectives'],
                max_action_steps=config_data.get('max_action_steps', 100),
                agents=agents,
                success_criteria=config_data['success_criteria'],
                relevant_game_context=config_data.get('relevant_game_context'),
                rounds=config_data.get('rounds'),
                shared_plan=config_data.get('shared_plan')
            )
        except Exception as e:
            self.logger.error(f"Error loading task config from {task_path}: {e}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.output_dir / f"task_runner_{self.run_timestamp}.log"
        error_log_file = self.output_dir / f"api_errors_{self.run_timestamp}.log"
        
        # Create logger
        self.logger = logging.getLogger('TaskRunner')
        
        # Set log level from environment variable or default to INFO
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO, 
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(log_level, logging.INFO))
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level_map.get(log_level, logging.INFO))  # Use same level as main logger
        
        # Create error file handler for API errors
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        
        # Create formatters - clean console, detailed file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter('%(message)s')  # Clean console output
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        error_handler.setFormatter(error_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        
        # Create observation logs directory
        self.observation_logs_dir = self.output_dir / "observation_logs"
        self.observation_logs_dir.mkdir(exist_ok=True)
        
        # Store error log file path for game tools
        self.error_log_file = error_log_file
    
    def log_message(self, message: str, color: int = 0):
        """Log message to both file logger and split-screen display"""
        # Always log to file
        self.logger.info(message)
        
        # Also log to split-screen display if available
        if self.use_split_screen and self.display:
            self.display.add_log(message, color)
            self.display.update_display()
    
    def log_chat(self, agent_name: str, message: str, username: str = ""):
        """Log chat message to split-screen display and extract for chat room"""
        # Always log to file
        self.logger.info(f"💬 {agent_name}: {message}")
        
        # Add to chat room if split-screen is available
        if self.use_split_screen and self.display:
            self.display.add_chat(agent_name, message, username)
            self.display.update_display()
    
    def log_agent_observation(self, agent_name: str, observation_data: dict, round_number: int = None):
        """Log agent observation to separate file"""
        try:
            # Create observation log file for this agent
            observation_file = self.observation_logs_dir / f"{agent_name}_observations_{self.run_timestamp}.jsonl"
            
            # Prepare observation record
            observation_record = {
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "round_number": round_number,
                "observation": observation_data
            }
            
            # Write to JSONL file (one JSON object per line)
            with open(observation_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(observation_record, ensure_ascii=False) + '\n')
            
            # Also log to main log file
            self.logger.info(f"📊 {agent_name} observation recorded (round {round_number})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log observation for {agent_name}: {e}")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful cleanup"""
        if self.cleanup_registered:
            return
            
        def signal_handler(signum, frame):
            self.log_message(f"🛑 Received signal {signum}, initiating cleanup...", color=2)
            if not self.use_split_screen:
                print(f"\n🛑 Interrupt received, cleaning up agents...")
            self._emergency_cleanup()
            if self.display:
                self.display.cleanup()
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination
        
        # Register atexit handler as backup
        atexit.register(self._emergency_cleanup)
        
        self.cleanup_registered = True
        self.logger.info("🛡️ Cleanup handlers registered")
    
    def _emergency_cleanup(self):
        """Emergency cleanup of all active agents"""
        if not self.active_agent_states:
            return
            
        self.logger.info("🧹 Starting emergency cleanup of active agents...")
        print("🧹 Logging out all active agents...")
        
        cleanup_count = 0
        for agent_name, agent_state in self.active_agent_states.items():
            if agent_state.console and agent_state.state != AgentState.FAILED:
                try:
                    self.logger.info(f"🔓 Logging out {agent_name}...")
                    logout_result = agent_state.console.agent.game_tools.logout_character()
                    self.logger.info(f"Logout result for {agent_name}: {logout_result}")
                    cleanup_count += 1
                    print(f"  ✅ {agent_name} logged out")
                except Exception as e:
                    self.logger.warning(f"Cleanup warning for {agent_name}: {str(e)}")
                    print(f"  ⚠️ {agent_name} logout failed: {str(e)}")
        
        if cleanup_count > 0:
            self.logger.info(f"🧹 Emergency cleanup completed: {cleanup_count} agents logged out")
            print(f"🧹 Cleanup completed: {cleanup_count} agents logged out")
        else:
            self.logger.info("🧹 No active agents to cleanup")
            print("🧹 No active agents to cleanup")
    
    def _create_agent_console(self, agent_name: str, agent_data: Dict[str, Any]) -> GameConsole:
        """Create a GameConsole instance for the agent"""
        
        # Parse location
        location = None
        if 'location' in agent_data:
            location = (agent_data['location']['x'], agent_data['location']['y'])

        # Random-spawn baseline: override the configured location with a seeded random one.
        if self.experiment.random_spawn:
            base_locations = []
            for adata in getattr(self, '_current_task_config_agents', {}).values():
                if 'location' in adata:
                    base_locations.append((adata['location']['x'], adata['location']['y']))
            if location is not None and not base_locations:
                base_locations = [location]
            location = self.experiment.random_location(base_locations)
            self.logger.info(f"🧪 random spawn for {agent_name}: {location}")
        
        # Parse skill levels
        skill_levels = agent_data.get('skill_levels', {})
        
        # Parse inventory items - convert from YAML format to console format
        inventory_items = []
        for item_data in agent_data.get('inventory_items', []):
            item_spec = f"{item_data['item']}:{item_data['count']}"
            if 'enchant' in item_data and item_data['enchant'] > 0:
                item_spec += f":{item_data['enchant']}"
            inventory_items.append(item_spec)
        
        # Parse equipped items - convert from YAML format to console format
        equipped_items = []
        for item_data in agent_data.get('equipped_items', []):
            item_spec = item_data['item']
            if item_data.get('count', 1) > 1:
                item_spec += f":{item_data['count']}"
            if 'enchant' in item_data and item_data['enchant'] > 0:
                enchant_suffix = f":{item_data['enchant']}" if item_data.get('count', 1) > 1 else f":1:{item_data['enchant']}"
                item_spec += enchant_suffix
            equipped_items.append(item_spec)
        
        # Create output file for this specific agent
        agent_log_file = self.output_dir / f"{agent_name}_{self.run_timestamp}.json"

        # Create prompts directory in output folder
        prompts_dir = self.output_dir / "prompts"
        prompts_dir.mkdir(exist_ok=True)

        # Create console with merged configuration
        console = GameConsole(
            username=agent_data.get('username', 'TaskAgent'),
            password=agent_data.get('password', 'password123'),
            provider=self.agent_config.provider,
            api_key=self.agent_config.llm.get('api_key'),
            model=self.agent_config.llm['model'],
            host=self.agent_config.game['host'],
            output_file=str(agent_log_file),
            initial_location=location,
            combat_levels=skill_levels,
            equipped_items=equipped_items,
            inventory_items=inventory_items,
            new_character=agent_data.get('new_character', False),
            dump_prompts=self.dump_prompts,
            llm_params=self.agent_config.llm
        )

        # Set custom prompts directory for this agent
        if self.dump_prompts:
            console.agent.prompts_dir = str(prompts_dir)

        # Override agent with configurable system prompt if provided
        if self.agent_config.system_prompt:
            console.agent = ConfigurableAgent(console.agent, self.agent_config.system_prompt)
            # Set prompts_dir for the wrapped agent too
            if self.dump_prompts:
                console.agent.base_agent.prompts_dir = str(prompts_dir)

        # Override max iterations (default to 50 if not in config)
        console.max_iterations = 50

        # Apply experiment communication restrictions to the agent.
        # For discussion-rounds, the per-round phase logic overrides this each round;
        # the initial setting here is the steady (post-discussion) state.
        self.experiment.apply_agent_restrictions(
            console.agent, **self.experiment.steady_state_restrictions()
        )

        return console
    
    def _is_chat_action(self, response: str) -> bool:
        """Check if the response contains a chat action"""
        # Look for chat tool usage in the response
        return 'chat(' in response or 'Global chat message sent:' in response or '"name": "chat"' in response
    
    def _extract_chat_message(self, response: str) -> str:
        """Extract the actual chat message content from agent response"""
        import re
        
        # Try different patterns to extract the chat message
        patterns = [
            r'Global chat message sent: ([^\n]+)',  # Result pattern
            r'\[TOOL_RESULT\] Global chat message sent: ([^\n]+)',  # Tool result pattern
            r'message=([^,)]+)',  # Argument pattern
            r'"message":\s*"([^"]+)"',  # JSON pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                message = match.group(1).strip()
                # Clean up the message
                if message.startswith('"') and message.endswith('"'):
                    message = message[1:-1]
                if message.startswith("'") and message.endswith("'"):
                    message = message[1:-1]
                return message
        
        return ""
    
    def _is_complete_action(self, response: str) -> bool:
        """Check if the response contains a complete action"""
        return 'complete(' in response or 'TASK_COMPLETE:' in response or '"name": "complete"' in response
    
    def _has_tool_execution(self, response: str) -> bool:
        """Check if the response contains any tool execution"""
        tool_indicators = [
            'TOOL CALLS', 'Calling ', 'Result:', 'tool call(s)', 
            'transfer_items(', 'move_character(', 'attack_entity(',
            'harvest_resource(', 'craft_item(', 'equip_item(',
            'login_character', 'logout_character', 'create_character',
            'chat(', 'observe(', 'complete(', 'teleport_character(',
            'collect(', 'craft(', 'attack(', 'equip(', 'enter(', 'stop(',
            '[TOOL EXECUTION]', 'tool_call_id', '"name":',
            'Response with', 'tool call(s):'  # Catch the BaseAgent output
        ]
        return any(indicator in response for indicator in tool_indicators)
    
    def _extract_tool_call_details(self, response: str) -> str:
        """Extract detailed tool call information from response"""
        import re
        import json
        
        # Look for tool call patterns (in order of specificity)
        patterns = [
            # New BaseAgent output patterns with detailed info
            r'\[TOOL_CALL_INFO\] (\w+)\(([^)]*)\)',  # New format: [TOOL_CALL_INFO] tool_name(args)
            # BaseAgent output patterns  
            r'Response with (\d+) tool call\(s\):.*?\[TOOL EXECUTION\]',  # BaseAgent tool execution
            r'Calling (\w+) with args: ({[^}]*})',  # Standard format: Calling chat with args: {'message': '...'}
            r'\[1\] Calling (\w+) with args: ({[^}]*})',  # Numbered format
            r'"name": "(\w+)".*?"arguments": ({[^}]*})',  # JSON format
            # Result patterns that indicate successful tool execution
            r'Global chat message sent: ([^\n]+)',  # Chat result pattern
            r'Character moved.*?distance: (\d+) tiles',  # Move result pattern  
            r'Character ([^\s]+) logged in successfully',  # Login result pattern
            r'Character teleported.*?to \((\d+), (\d+)\)',  # Teleport result pattern
            r'Successfully equipped.*?(\w+)',  # Equip result pattern
            r'Successfully crafted.*?(\w+)',  # Craft result pattern
            r'TASK_COMPLETE: (.+)',  # Complete result pattern
            r'(\w+)\(([^)]*)\)',  # Simple function call format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                # Handle new TOOL_CALL_INFO pattern (most specific)
                if 'TOOL_CALL_INFO' in pattern:
                    tool_name = match.group(1)
                    args = match.group(2)
                    # Args are already formatted in BaseAgent, just return them
                    return f"{tool_name}({args})"
                # Handle BaseAgent tool execution pattern
                elif 'Response with' in pattern and 'tool call' in pattern:
                    return "tool_execution(detected)"
                # Handle specific result patterns
                elif 'Global chat message sent:' in pattern:
                    message = match.group(1)
                    return f"chat(message='{message}')"
                elif 'Character moved' in pattern:
                    distance = match.group(1)
                    return f"move_character(distance={distance} tiles)"
                elif 'logged in successfully' in pattern:
                    username = match.group(1)
                    return f"login_character(username='{username}')"
                elif 'Character teleported' in pattern:
                    x, y = match.group(1), match.group(2)
                    return f"teleport_character(x={x}, y={y})"
                elif 'Successfully equipped' in pattern:
                    item = match.group(1)
                    return f"equip(item='{item}')"
                elif 'Successfully crafted' in pattern:
                    item = match.group(1)
                    return f"craft(item='{item}')"
                elif 'TASK_COMPLETE:' in pattern:
                    return "complete(task_finished)"
                else:
                    tool_name = match.group(1)
                    try:
                        if len(match.groups()) > 1:
                            args = match.group(2)
                            # Clean up arguments for display
                            if args.startswith('{') and args.endswith('}'):
                                try:
                                    parsed_args = json.loads(args)
                                    # Format key arguments for display
                                    key_args = []
                                    for k, v in parsed_args.items():
                                        if isinstance(v, str) and len(v) > 30:
                                            v = v[:30] + '...'
                                        key_args.append(f"{k}={v}")
                                    formatted_args = ', '.join(key_args[:3])  # Show max 3 args
                                    if len(parsed_args) > 3:
                                        formatted_args += ', ...'
                                except:
                                    formatted_args = args[:50] + '...' if len(args) > 50 else args
                            else:
                                formatted_args = args[:50] + '...' if len(args) > 50 else args
                            return f"{tool_name}({formatted_args})"
                        else:
                            return f"{tool_name}(...)"
                    except:
                        return f"{tool_name}(...)"
        
        # Fallback: look for common tool names in response
        tool_patterns = [
            ('chat', r'Global chat message sent'),
            ('move_character', r'Character moved'),
            ('transfer_items', r'transfer'),
            ('craft_item', r'craft'),
            ('attack_entity', r'attack'),
            ('harvest_resource', r'harvest'),
            ('equip_item', r'equip'),
            ('complete', r'TASK_COMPLETE|complete'),
            ('sleep', r'Slept for \d+ second'),
            ('observe', r'observe')
        ]
        
        for tool_name, pattern in tool_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return f"{tool_name}(...)"
        
        return "unknown_tool(...)"
    
    def _get_agent_status_details(self, agent_state: AgentExecutionState) -> str:
        """Get detailed status information for an agent including level, location, HP, MP"""
        try:
            # Get player status from the console
            status_info = agent_state.console.get_player_status()
            if status_info and "Status: Player data not available" not in status_info:
                return status_info
            else:
                # Fallback to basic status
                return f"📊 Status: Session {'active' if agent_state.console.agent.game_tools.token else 'inactive'}"
        except Exception as e:
            return f"📊 Status: Error getting details - {str(e)[:30]}..."

    def _is_agent_dead(self, agent_state: AgentExecutionState) -> bool:
        """Check if an agent is dead (HP <= 0)"""
        try:
            if not agent_state.console or not agent_state.console.agent.game_tools:
                return False

            # Get observation to check HP
            result = agent_state.console.agent.game_tools.observe_environment({"radius": 1})

            if isinstance(result, str) and "Environment observation" in result:
                import re
                import json
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    player_status = data.get("playerStatus", {})
                    hp = player_status.get("hitPoints", 100)  # Default to 100 if not found
                    return hp <= 0
            return False
        except Exception as e:
            self.logger.warning(f"Error checking agent death status: {e}")
            return False

    def _apply_comm_phase(self, agent_states: Dict[str, AgentExecutionState], round_count: int):
        """Adjust per-agent communication restrictions for the current round.

        Only meaningful for the --discussion-rounds baseline:
          rounds 1..N  -> chat-only phase (all action tools disabled, chat enabled)
          rounds > N   -> communication fully cut
        For all other configurations this is a no-op (restrictions were set at console creation).
        """
        exp = self.experiment
        if exp.discussion_rounds <= 0:
            return

        in_discussion = round_count <= exp.discussion_rounds
        for agent_state in agent_states.values():
            if not agent_state.console:
                continue
            if in_discussion:
                # Chat-only: agents can talk and see each other, but cannot act.
                exp.apply_agent_restrictions(
                    agent_state.console.agent,
                    allow_chat=True,
                    allow_transfer=False,
                    hide_chat_history=False,
                    hide_other_players=False,
                    discussion_phase=True,
                )
            else:
                # Post-discussion: communication fully cut.
                exp.apply_agent_restrictions(
                    agent_state.console.agent,
                    allow_chat=False,
                    allow_transfer=False,
                    hide_chat_history=True,
                    hide_other_players=True,
                    discussion_phase=False,
                )

    def _execute_agent_turn(self, agent_state: AgentExecutionState, task_prompt: str, max_action_steps: int) -> Tuple[bool, str]:
        """
        Execute a single tool call for an agent.
        Returns (should_continue, response)
        """
        try:
            agent_state.state = AgentState.ACTIVE
            if agent_state.start_time is None:
                agent_state.start_time = time.time()
            
            # Execute exactly one tool call.
            if self.experiment.random_agent:
                # Random baseline: pick a uniformly random legal action (no LLM).
                if not hasattr(self, '_random_policy'):
                    self._random_policy = RandomAgentPolicy(self.experiment)
                response = self._random_policy.act(agent_state.console)
            else:
                response = agent_state.console.agent.execute_single_tool_call(task_prompt)
            agent_state.last_response = response
            
            # Check if this was a complete action
            if self._is_complete_action(response):
                agent_state.state = AgentState.COMPLETED
                agent_state.completion_reason = "Agent executed complete action"
                agent_state.end_time = time.time()
                return False, response
            
            # Check if this was a chat action (doesn't count towards action limit)
            if self._is_chat_action(response):
                agent_state.chat_count += 1
                # Chat actions don't count towards action limit, so continue
                # Return True to continue, but agent has completed this tool call
                return True, response
            
            # Check if this had any tool execution
            if self._has_tool_execution(response):
                agent_state.action_count += 1
                
                # Check if agent reached action limit
                if agent_state.action_count >= max_action_steps:
                    agent_state.state = AgentState.COMPLETED
                    agent_state.completion_reason = f"Reached maximum action steps ({max_action_steps})"
                    agent_state.end_time = time.time()
                    return False, response
                
                # Agent executed a tool and should continue, but this tool call is done
                return True, response
            
            # If no tool was executed, this might be an error or planning response
            # Still count it and continue (agent might be thinking/planning)
            return True, response
            
        except Exception as e:
            agent_state.state = AgentState.FAILED
            agent_state.error_message = str(e)
            agent_state.end_time = time.time()
            return False, f"Agent execution failed: {str(e)}"
    
    def _initialize_agents(self, task_config: TaskConfig) -> Dict[str, AgentExecutionState]:
        """Initialize all agents for multi-agent execution"""
        agent_states = {}
        
        for agent_name, agent_data in task_config.agents.items():
            self.logger.info(f"🤖 Initializing agent: {agent_name}")
            
            try:
                # Create agent console
                console = self._create_agent_console(agent_name, agent_data)
                
                # Perform login and initial state setup
                if console.new_character:
                    self.logger.info(f"Force creating new character for {agent_name}")
                    login_result = console.handle_new_character_creation()
                else:
                    # Try master password first, then fallback to original password
                    login_result = console.agent.game_tools.login_character({
                        "username": console.username,
                        "password": MASTER_PASSWORD
                    })
                    
                    # If master password failed, try original password
                    if not ("successfully" in login_result.lower() and "token obtained" in login_result.lower()):
                        self.logger.warning(f"Master password login failed for {agent_name}, trying original password")
                        login_result = console.agent.game_tools.login_character({
                            "username": console.username,
                            "password": console.password
                        })
                self.logger.info(f"Login result for {agent_name}: {login_result}")
                
                # Check if login was successful (be more flexible with success detection)
                login_successful = False
                if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                    login_successful = True
                elif console.new_character and "token" in login_result and not ("failed" in login_result.lower() or "error" in login_result.lower()):
                    # For new character creation, be more lenient about success detection
                    login_successful = True
                    self.logger.info(f"Detected successful character creation for {agent_name} (lenient check)")
                
                # Verify token was actually obtained (double-check beyond login message parsing)
                has_token = console.agent.game_tools and console.agent.game_tools.token

                if not has_token:
                    self.logger.error(f"❌ Agent {agent_name} has no token after login attempt - marking as FAILED")
                    agent_states[agent_name] = AgentExecutionState(
                        agent_name=agent_name,
                        console=console,
                        state=AgentState.FAILED,
                        action_count=0,
                        chat_count=0,
                        last_response="",
                        error_message="No token obtained - server may be unreachable"
                    )
                    continue

                # Apply initial state if login successful
                if login_successful:
                    initial_state_results = console.apply_initial_state()
                    if initial_state_results:
                        self.logger.info(f"Applied initial state for {agent_name}: {len(initial_state_results)} operations")
                else:
                    self.logger.warning(f"Login may have failed for {agent_name}, but continuing anyway")

                # Create agent execution state
                agent_states[agent_name] = AgentExecutionState(
                    agent_name=agent_name,
                    console=console,
                    state=AgentState.WAITING,
                    action_count=0,
                    chat_count=0,
                    last_response=""
                )
                
                # Record initial observation for this agent ONLY if login was successful
                if login_successful:
                    try:
                        if console.agent.game_tools and console.agent.game_tools.token:
                            # Trigger an initial observation
                            initial_observation = console.agent.game_tools.observe_environment({"radius": 64})
                            observation_data = console.agent.game_tools.get_last_observation_data()
                            if observation_data:
                                self.log_agent_observation(agent_name, observation_data, 0)  # Round 0 for initial
                                self.logger.info(f"📊 Initial observation recorded for {agent_name}")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to record initial observation for {agent_name}: {e}")
                else:
                    self.logger.warning(f"⚠️ Skipping initial observation for {agent_name} due to login failure")
                
                self.logger.info(f"✅ Agent {agent_name} initialized successfully")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize agent {agent_name}: {e}")
                # Create failed state
                agent_states[agent_name] = AgentExecutionState(
                    agent_name=agent_name,
                    console=None,
                    state=AgentState.FAILED,
                    action_count=0,
                    chat_count=0,
                    last_response="",
                    error_message=str(e)
                )
        
        return agent_states
    
    def _cleanup_agents(self, agent_states: Dict[str, AgentExecutionState]):
        """Cleanup agents after execution"""
        for agent_name, agent_state in agent_states.items():
            if agent_state.console and agent_state.state != AgentState.FAILED:
                try:
                    logout_result = agent_state.console.agent.game_tools.logout_character()
                    self.logger.info(f"Logout result for {agent_name}: {logout_result}")
                except Exception as e:
                    self.logger.warning(f"Logout warning for {agent_name}: {str(e)}")
    
    def run_single_task(self, task_path: str) -> Dict[str, Any]:
        """Run a single task from configuration file with multi-agent support"""
        self.logger.info(f"🎯 Starting task: {task_path}")
        
        # Load task configuration
        task_config = self._load_task_config(task_path)
        
        # Make agents available for spawn-region computation in _create_agent_console
        self._current_task_config_agents = task_config.agents
        
        # Initialize trajectory data
        self._init_trajectory(task_path, task_config)
        
        self.logger.info(f"Task: {task_config.name}")
        self.logger.info(f"Description: {task_config.description}")
        self.logger.info(f"Primary objective: {task_config.objectives['primary']}")
        self.logger.info(f"Agents: {list(task_config.agents.keys())}")
        
        # Single-agent upper-bound baseline: collapse a multi-agent task into one merged agent.
        if self.experiment.single_agent_upper_bound and len(task_config.agents) > 1:
            self.logger.info("🧪 single-agent upper bound: running the entire task with one solo merged agent (no other agents, no communication)")
            self.experiment.collapse_to_single_agent(task_config)
            self.logger.info(f"Collapsed agents: {list(task_config.agents.keys())}")

        # Check if this is a multi-agent task
        if len(task_config.agents) > 1:
            return self._run_multi_agent_task(task_config)
        else:
            return self._run_single_agent_task(task_config)
    
    def _run_single_agent_task(self, task_config: TaskConfig) -> Dict[str, Any]:
        """Run task with single agent (original behavior)"""
        results = {}
        
        # Setup signal handlers for cleanup
        self._setup_signal_handlers()
        
        # Execute task for each agent (should be only one)
        for agent_name, agent_data in task_config.agents.items():
            self.logger.info(f"🤖 Running task with agent: {agent_name}")
            
            try:
                # Create agent console
                console = self._create_agent_console(agent_name, agent_data)
                
                # Track agent for cleanup
                self.active_agent_states[agent_name] = AgentExecutionState(
                    agent_name=agent_name,
                    console=console,
                    state=AgentState.ACTIVE,
                    action_count=0,
                    chat_count=0,
                    last_response=""
                )
                
                # Build task prompt from configuration
                task_prompt = self._build_task_prompt(task_config)
                
                # Execute the task
                start_time = time.time()
                
                self.logger.info(f"Executing task: {task_prompt}")
                
                # Auto-login first - try master password then fallback
                try:
                    # Try master password first
                    login_result = console.agent.game_tools.login_character({
                        "username": console.username,
                        "password": MASTER_PASSWORD
                    })
                    
                    # If master password failed, try original password
                    if not ("successfully" in login_result.lower() and "token obtained" in login_result.lower()):
                        self.logger.warning("Master password login failed, trying original password")
                        login_result = console.agent.game_tools.login_character({
                            "username": console.username,
                            "password": console.password
                        })
                    
                    self.logger.info(f"Login result: {login_result}")
                    
                    # Apply initial state if login successful
                    if "successfully" in login_result.lower() and "token obtained" in login_result.lower():
                        initial_state_results = console.apply_initial_state()
                        if initial_state_results:
                            self.logger.info(f"Applied initial state: {len(initial_state_results)} operations")
                    
                    # Execute the task via agent
                    final_response = console.agent.process_user_input(task_prompt)
                    
                    # Try to logout after task completion
                    try:
                        logout_result = console.agent.game_tools.logout_character()
                        self.logger.info(f"Logout result: {logout_result}")
                        # Clear from active agents since we logged out
                        self.active_agent_states.pop(agent_name, None)
                    except Exception as e:
                        self.logger.warning(f"Logout warning: {str(e)}")
                    
                    success = True
                    
                except Exception as e:
                    self.logger.error(f"Task execution error: {str(e)}")
                    final_response = f"Task execution failed: {str(e)}"
                    success = False
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Store results
                results[agent_name] = {
                    'success': success,
                    'final_message': final_response,
                    'iterations': console.agent.tool_call_count if hasattr(console.agent, 'tool_call_count') else 0,
                    'duration_seconds': duration,
                    'log_file': str(console.output_file) if hasattr(console, 'output_file') and console.output_file else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"✅ Agent {agent_name} completed task in {duration:.2f}s")
                self.logger.info(f"Success: {results[agent_name]['success']}")
                self.logger.info(f"Iterations: {results[agent_name]['iterations']}")
                
            except Exception as e:
                self.logger.error(f"❌ Error running task with agent {agent_name}: {e}")
                results[agent_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Save task summary
        self._save_task_summary(task_config, results)
        
        return results
    
    def _run_multi_agent_task(self, task_config: TaskConfig) -> Dict[str, Any]:
        """Run a multi-agent task with synchronized tool-call-level execution"""
        self.logger.info(f"🎯 Starting multi-agent task execution")
        
        start_time = time.time()
        
        # Setup signal handlers for cleanup
        self._setup_signal_handlers()
        
        # Initialize all agents
        self.logger.info(f"🔄 Initializing {len(task_config.agents)} agents...")
        agent_states = self._initialize_agents(task_config)
        
        # Store agent states for cleanup
        self.active_agent_states = agent_states
        
        # Check if any agents failed to initialize
        failed_agents = [name for name, state in agent_states.items() if state.state == AgentState.FAILED]
        if failed_agents:
            self.logger.error(f"❌ Failed to initialize agents: {failed_agents}")

            # Get error details
            error_details = []
            for name in failed_agents:
                state = agent_states[name]
                error_details.append(f"{name}: {state.error_message or 'Unknown error'}")

            # Check if this looks like a server connectivity issue
            server_down = any("token" in (s.error_message or "").lower() or "unreachable" in (s.error_message or "").lower()
                            for s in agent_states.values() if s.state == AgentState.FAILED)

            if server_down:
                self.logger.error("❌ SERVER CONNECTIVITY ISSUE DETECTED - agents cannot connect to game server")
                self.logger.error("   Please check if the game server is running at the configured host")

        # Count working agents (those with valid tokens)
        working_agents = {name: state for name, state in agent_states.items() if state.state != AgentState.FAILED}

        if not working_agents:
            self.logger.error("❌ No agents available for execution - ABORTING TASK")
            self.logger.error("   All agents failed to initialize. This usually means:")
            self.logger.error("   1. Game server is not running or unreachable")
            self.logger.error("   2. Network connectivity issues")
            self.logger.error("   3. Authentication/login failures")
            print("\n" + "=" * 70)
            print("❌ TASK ABORTED: All agents failed to initialize")
            print("=" * 70)
            print("Error details:")
            for detail in error_details:
                print(f"  - {detail}")
            print("\nPlease check:")
            print("  1. Is the game server running?")
            print("  2. Can you reach the server at the configured host?")
            print("  3. Are the agent credentials correct?")
            print("=" * 70 + "\n")

            # Save a summary even for failed initialization
            self._save_task_summary(task_config, {
                "_initialization_failed": True,
                "_error": "All agents failed to initialize - server may be unreachable",
                "_failed_agents": error_details
            })

            return {"error": "All agents failed to initialize", "details": error_details}

        # Update agent_states to only include working agents
        agent_states = working_agents
        
        # Note: Task prompts will be built per agent with team context
        
        # Execute synchronized tool-call-level execution
        self.logger.info(f"🔄 Starting synchronized tool-call-level execution...")
        self.logger.info(f"   Each agent will execute exactly one tool call per turn")
        
        max_rounds = self.experiment.resolve_max_rounds(task_config.rounds)  # CLI > YAML > 55
        round_count = 0
        agent_order = list(agent_states.keys())  # Fixed order for round-robin
        if self.experiment.discussion_rounds > 0:
            self.logger.info(f"🧪 discussion phase: first {self.experiment.discussion_rounds} rounds are chat-only, then communication is cut")
        
        while round_count < max_rounds:
            round_count += 1
            
            # Apply discussion-phase communication gating for this round.
            self._apply_comm_phase(agent_states, round_count)

            # Log round header with better formatting
            self.log_message("=" * 80)
            self.log_message(f"🔄 ROUND {round_count}", color=4)
            self.log_message("=" * 80)
            
            # Initialize round data for trajectory
            round_data = {
                'round': round_count,
                'actions': []
            }
            
            # Track if any agent is still active this round
            any_agent_active = False
            
            # Execute exactly one tool call for each agent in order
            for agent_name in agent_order:
                agent_state = agent_states[agent_name]

                # Skip agents that are already completed or failed
                if agent_state.state in [AgentState.COMPLETED, AgentState.FAILED]:
                    self.log_message(f"  🤖 {agent_name} (skipped - {agent_state.state.value})", color=3)
                    continue

                # Check if agent is dead (HP <= 0) before executing their turn
                if self._is_agent_dead(agent_state):
                    agent_state.state = AgentState.FAILED
                    agent_state.error_message = "Agent died (HP <= 0)"
                    agent_state.end_time = time.time()
                    self.log_message(f"  💀 {agent_name} is DEAD (HP <= 0) - marked as failed", color=1)
                    continue

                self.log_message(f"  🤖 {agent_name} executing tool call...", color=6)
                
                # Build agent-specific task prompt with team context
                agent_task_prompt = self._build_task_prompt(task_config, agent_name, agent_states)
                
                # Execute agent turn (exactly one tool call)
                should_continue, response = self._execute_agent_turn(
                    agent_state, agent_task_prompt, task_config.max_action_steps
                )
                
                # Collect trajectory data for this agent action
                action_data = self._collect_action_data(agent_name, agent_state, response)
                round_data['actions'].append(action_data)
                
                # Extract and display detailed tool call information
                if self._has_tool_execution(response) or self._is_chat_action(response) or self._is_complete_action(response):
                    tool_details = self._extract_tool_call_details(response)
                    self.log_message(f"    🔧 Tool called: {tool_details}", color=1)
                    
                    # Extract chat message for chat room if this is a chat action
                    if self._is_chat_action(response):
                        chat_message = self._extract_chat_message(response)
                        if chat_message:
                            # Get username from agent state
                            username = getattr(agent_state.console, 'username', '')
                            self.log_chat(agent_name, chat_message, username)
                else:
                    self.log_message(f"    💭 No tool call (thinking/planning)", color=3)
                
                # Get detailed status information
                detailed_status = self._get_agent_status_details(agent_state)
                
                # Log the agent's current state with detailed info
                basic_state = f"State: {agent_state.state.value} | Actions: {agent_state.action_count} | Chats: {agent_state.chat_count}"
                self.log_message(f"    📊 {basic_state}", color=4)
                self.log_message(f"    {detailed_status}", color=4)
                
                # Extract and display tool call info and result separately
                tool_call_info = ""
                tool_result = ""
                
                # Extract TOOL_CALL_INFO
                import re
                tool_call_match = re.search(r'\[TOOL_CALL_INFO\] ([^\n]+)', response)
                if tool_call_match:
                    tool_call_info = tool_call_match.group(1)
                
                # Extract TOOL_RESULT  
                tool_result_match = re.search(r'\[TOOL_RESULT\] ([^\n]+)', response)
                if tool_result_match:
                    tool_result = tool_result_match.group(1)
                
                # Display tool call info and result on separate lines
                if tool_call_info:
                    self.log_message(f"    🔧 Tool call: {tool_call_info}", color=4)
                if tool_result:
                    self.log_message(f"    ✅ Result: {tool_result}", color=1)
                
                # Show other response content if available (excluding tool markers)
                clean_response = re.sub(r'\[TOOL_CALL_INFO\].*?\n?', '', response)
                clean_response = re.sub(r'\[TOOL_RESULT\].*?\n?', '', clean_response)
                if clean_response.strip():
                    response_preview = clean_response[:100].replace('\n', ' ').strip()
                    if response_preview:
                        response_preview = response_preview + '...' if len(clean_response) > 100 else response_preview
                        self.log_message(f"    💭 Content: {response_preview}", color=0)
                
                # Record agent observation if available
                # IMPORTANT: Take a fresh observation AFTER the action is executed
                try:
                    if agent_state.console and agent_state.console.agent.game_tools:
                        # Add a small delay to ensure the game server has processed the action
                        time.sleep(0.5)
                        
                        # Take a fresh observation to capture the state AFTER the action
                        agent_state.console.agent.game_tools.observe_environment({"radius": 64})
                        observation_data = agent_state.console.agent.game_tools.get_last_observation_data()
                        
                        if observation_data:
                            self.log_agent_observation(agent_name, observation_data, round_count)
                except Exception as e:
                    self.logger.error(f"❌ Failed to record observation for {agent_name}: {e}")
                
                # CRITICAL: After each agent executes ONE tool call, we move to the next agent
                # regardless of whether they want to continue or not
                if should_continue:
                    any_agent_active = True
                
                # Force move to next agent after exactly one tool call
            
            # Check if all agents are completed or failed
            active_agents = [name for name, state in agent_states.items() 
                           if state.state not in [AgentState.COMPLETED, AgentState.FAILED]]
            
            # Round summary
            completed_agents = [name for name, state in agent_states.items() if state.state == AgentState.COMPLETED]
            failed_agents = [name for name, state in agent_states.items() if state.state == AgentState.FAILED]
            
            self.logger.info(f"📊 Round {round_count} Summary: Active={len(active_agents)}, Completed={len(completed_agents)}, Failed={len(failed_agents)}")
            print(f"📊 Round {round_count} Summary: Active={len(active_agents)}, Completed={len(completed_agents)}, Failed={len(failed_agents)}")
            
            # Add this round's data to trajectory
            self.trajectory_data['rounds'].append(round_data)

            # Early stopping check: verify task success every 3 rounds (starting from round 5)
            # This saves tokens and time by stopping when the task is already complete
            if round_count >= 5 and round_count % 3 == 0:
                task_success, verify_msg = self._check_task_success_early()
                if task_success:
                    self.logger.info(f"🎉 EARLY STOPPING: Task verified as SUCCESS at round {round_count}!")
                    self.logger.info(f"   Verification: {verify_msg}")
                    print(f"\n{'='*70}")
                    print(f"🎉 EARLY STOPPING: Task completed successfully!")
                    print(f"   Round: {round_count}/{max_rounds}")
                    print(f"   Verification: {verify_msg}")
                    print(f"   Saved {max_rounds - round_count} rounds of execution")
                    print(f"{'='*70}\n")
                    # Mark all active agents as completed
                    for agent_state in agent_states.values():
                        if agent_state.state not in [AgentState.COMPLETED, AgentState.FAILED]:
                            agent_state.state = AgentState.COMPLETED
                            agent_state.completion_reason = f"Task success verified at round {round_count}"
                            agent_state.end_time = time.time()
                    break

            if not active_agents:
                self.logger.info(f"✅ All agents completed or failed after {round_count} rounds")
                print(f"✅ All agents completed or failed after {round_count} rounds")
                break
        else:
            self.logger.warning(f"⚠️ Execution stopped after maximum rounds ({max_rounds})")
            # Mark remaining active agents as completed due to timeout
            for agent_state in agent_states.values():
                if agent_state.state == AgentState.WAITING:
                    agent_state.state = AgentState.COMPLETED
                    agent_state.completion_reason = "Maximum rounds reached"
                    agent_state.end_time = time.time()
        
        # Cleanup agents (normal completion)
        self._cleanup_agents(agent_states)
        
        # Clear active agent states since we've cleaned up
        self.active_agent_states = {}
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Compile results
        results = {}
        for agent_name, agent_state in agent_states.items():
            agent_duration = 0
            if agent_state.start_time and agent_state.end_time:
                agent_duration = agent_state.end_time - agent_state.start_time
            elif agent_state.start_time:
                agent_duration = end_time - agent_state.start_time
            
            results[agent_name] = {
                'success': agent_state.state == AgentState.COMPLETED,
                'final_message': agent_state.last_response,
                'state': agent_state.state.value,
                'action_count': agent_state.action_count,
                'chat_count': agent_state.chat_count,
                'completion_reason': agent_state.completion_reason,
                'error_message': agent_state.error_message,
                'duration_seconds': agent_duration,
                'log_file': str(agent_state.console.output_file) if agent_state.console and hasattr(agent_state.console, 'output_file') and agent_state.console.output_file else None,
                'timestamp': datetime.now().isoformat()
            }
        
        # Run final verification check
        final_verification_success, final_verification_msg = self._check_task_success_early()

        # Add multi-agent specific metrics
        multi_agent_metrics = {
            'total_duration_seconds': total_duration,
            'total_rounds': round_count,
            'max_rounds': max_rounds,
            'total_agents': len(agent_states),
            'successful_agents': len([r for r in results.values() if r['success']]),
            'failed_agents': len([r for r in results.values() if not r['success']]),
            'total_actions': sum(r['action_count'] for r in results.values()),
            'total_chats': sum(r['chat_count'] for r in results.values()),
            'task_verified_success': final_verification_success,
            'task_verification_message': final_verification_msg,
            'early_stopped': round_count < max_rounds and final_verification_success,
            'rounds_saved': max_rounds - round_count if final_verification_success else 0
        }
        
        self.logger.info(f"📊 Multi-agent execution completed:")
        self.logger.info(f"  Duration: {total_duration:.2f}s")
        self.logger.info(f"  Rounds: {round_count}/{max_rounds}")
        self.logger.info(f"  Task Verified: {'✅ SUCCESS' if final_verification_success else '❌ FAILED'}")
        self.logger.info(f"  Verification: {final_verification_msg}")
        self.logger.info(f"  Successful agents: {multi_agent_metrics['successful_agents']}/{multi_agent_metrics['total_agents']}")
        self.logger.info(f"  Total actions: {multi_agent_metrics['total_actions']}")
        self.logger.info(f"  Total chats: {multi_agent_metrics['total_chats']}")
        
        # Print detailed final status for each agent
        print(f"\n📊 FINAL AGENT STATUS:")
        print("=" * 70)
        self.logger.info("📊 Final Agent Status Details:")
        
        for agent_name, agent_state in agent_states.items():
            duration = 0
            if agent_state.start_time and agent_state.end_time:
                duration = agent_state.end_time - agent_state.start_time
            elif agent_state.start_time:
                duration = end_time - agent_state.start_time
            
            # Get final detailed status
            final_status = self._get_agent_status_details(agent_state)
            status_emoji = "✅" if agent_state.state == AgentState.COMPLETED else "❌" if agent_state.state == AgentState.FAILED else "⏸️"
            
            print(f"  {status_emoji} {agent_name}: {agent_state.state.value}")
            print(f"    📈 Actions: {agent_state.action_count} | Chats: {agent_state.chat_count} | Duration: {duration:.1f}s")
            print(f"    {final_status}")
            if agent_state.completion_reason:
                print(f"    🏁 {agent_state.completion_reason}")
            if agent_state.error_message:
                print(f"    ❌ Error: {agent_state.error_message}")
            print()
            
            # Also log to file
            self.logger.info(f"  {agent_name}: {agent_state.state.value}")
            self.logger.info(f"    Actions: {agent_state.action_count}, Chats: {agent_state.chat_count}, Duration: {duration:.1f}s")
            self.logger.info(f"    {final_status}")
            if agent_state.completion_reason:
                self.logger.info(f"    Completion: {agent_state.completion_reason}")
            if agent_state.error_message:
                self.logger.info(f"    Error: {agent_state.error_message}")
        
        # Add metrics to results
        results['_multi_agent_metrics'] = multi_agent_metrics

        # Print final verification result
        print("=" * 70)
        verification_emoji = "✅" if final_verification_success else "❌"
        print(f"{verification_emoji} TASK VERIFICATION: {'SUCCESS' if final_verification_success else 'FAILED'}")
        print(f"   {final_verification_msg}")
        if multi_agent_metrics['early_stopped']:
            print(f"   ⚡ Early stopped at round {round_count}, saved {multi_agent_metrics['rounds_saved']} rounds")
        print("=" * 70)

        # Save task summary
        self._save_task_summary(task_config, results)
        
        return results
    
    def run_task_folder(self, folder_path: str) -> Dict[str, Any]:
        """Run all tasks in a folder"""
        self.logger.info(f"📁 Running all tasks in folder: {folder_path}")
        
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Task folder not found: {folder_path}")
        
        # Find all YAML task files
        task_files = list(folder.glob("*.yaml")) + list(folder.glob("*.yml"))
        
        if not task_files:
            self.logger.warning(f"No task files found in {folder_path}")
            return {}
        
        self.logger.info(f"Found {len(task_files)} task files")

        # Sort task files numerically by task number (e.g., task_01, task_02, ..., task_100)
        def get_task_number(filepath):
            """Extract numeric task number from filename for proper sorting"""
            import re
            match = re.search(r'task_(\d+)', filepath.name)
            return int(match.group(1)) if match else 0

        task_files_sorted = sorted(task_files, key=get_task_number)

        all_results = {}

        for task_file in task_files_sorted:
            self.logger.info(f"📋 Processing task file: {task_file.name}")
            
            try:
                task_results = self.run_single_task(str(task_file))
                all_results[task_file.name] = task_results
                
            except Exception as e:
                self.logger.error(f"❌ Error processing task file {task_file.name}: {e}")
                all_results[task_file.name] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Save folder summary
        self._save_folder_summary(folder_path, all_results)
        
        return all_results
    
    def _build_task_prompt(self, task_config: TaskConfig, agent_name: str = None, agent_states: Dict[str, 'AgentExecutionState'] = None) -> str:
        """Build task prompt from configuration using Jinja2 template if available"""
        exp = self.experiment
        comms_off = exp.cuts_communication

        # Resolve the task-specific document (honor --no-task-docs).
        relevant_context = None if exp.no_task_docs else task_config.relevant_game_context

        # Resolved round budget (CLI > task YAML > default).
        resolved_max_rounds = exp.resolve_max_rounds(task_config.rounds)

        # Check if we have a user prompt template in the agent config
        if hasattr(self, 'agent_config') and self.agent_config.user_prompt_template:
            # Use Jinja2 template
            template = Template(self.agent_config.user_prompt_template)
            
            # Prepare template variables
            template_vars = {
                'task_name': task_config.name,
                'task_description': task_config.description,
                'primary_objective': task_config.objectives['primary'],
                'secondary_objectives': task_config.objectives.get('secondary', []),
                'relevant_game_context': relevant_context,
                'success_criteria': task_config.success_criteria,
                'objectives': task_config.objectives,  # Full objectives dict for backward compatibility
                'max_rounds': resolved_max_rounds
            }
            
            # Add team information for multi-agent tasks
            if agent_states and len(agent_states) > 1:
                # Get actual usernames from agent states
                current_agent_username = agent_states[agent_name].console.username if agent_name in agent_states else agent_name
                other_usernames = []
                
                for name, state in agent_states.items():
                    if name != agent_name:
                        username = state.console.username if hasattr(state, 'console') and state.console else name
                        other_usernames.append(username)

                # --no-roles: present a generic identity so role isn't inferred from the username.
                if exp.no_roles and agent_name:
                    agent_index = list(agent_states.keys()).index(agent_name) + 1 if agent_name in agent_states else 1
                    current_agent_username = f"Agent_{agent_index}"
                    other_usernames = [f"Agent_{i + 1}" for i in range(len(agent_states)) if i != agent_index - 1]

                # When communication is cut, other agents are not visible at all.
                if comms_off:
                    other_usernames = []

                template_vars.update({
                    'total_agents': len(agent_states),
                    'agent_username': current_agent_username,
                    'other_agent_usernames': other_usernames
                })
                
                # Add agent status information (only when communication / visibility is on)
                if agent_states and not comms_off:
                    agent_status_info = []
                    for name, state in agent_states.items():
                        username = state.console.username if hasattr(state, 'console') and state.console else name
                        status_entry = {
                            'username': username,
                            'status': state.state.value if hasattr(state, 'state') else 'unknown'
                        }
                        # Add HP and MP information using cached observation data
                        try:
                            if hasattr(state, 'console') and state.console and hasattr(state.console, 'agent') and state.console.agent.game_tools:
                                # Use cached observation data (much faster than calling observe_environment)
                                observation_data = state.console.agent.game_tools.get_last_observation_data()
                                if observation_data and isinstance(observation_data, dict):
                                    player_status = observation_data.get("playerStatus", {})
                                    if player_status:
                                        status_entry['hp'] = player_status.get("hitPoints", "?")
                                        status_entry['max_hp'] = player_status.get("maxHitPoints", "?")
                                        status_entry['mp'] = player_status.get("mana", "?")
                                        status_entry['max_mp'] = player_status.get("maxMana", "?")
                                        self.logger.debug(f"Got HP/MP for {username}: HP={status_entry.get('hp')}/{status_entry.get('max_hp')}, MP={status_entry.get('mp')}/{status_entry.get('max_mp')}")
                                    else:
                                        self.logger.debug(f"No playerStatus in observation for {username}")
                                else:
                                    self.logger.debug(f"No cached observation data for {username}")
                        except Exception as e:
                            # If we can't get HP/MP, log the error for debugging
                            self.logger.debug(f"Failed to get HP/MP for {username}: {e}")

                        if hasattr(state, 'last_response') and state.last_response:
                            # Extract last action from response if available
                            if 'Tool called:' in str(state.last_response):
                                action_start = str(state.last_response).find('Tool called:') + 12
                                action_end = str(state.last_response).find('\n', action_start)
                                if action_end == -1:
                                    action_end = action_start + 50
                                status_entry['last_action'] = str(state.last_response)[action_start:action_end].strip()

                        agent_status_info.append(status_entry)
                        self.logger.debug(f"Added status entry for {username}: {status_entry}")

                    template_vars['agent_status_info'] = agent_status_info
                    self.logger.debug(f"Total agent_status_info entries: {len(agent_status_info)}")
                    print(f"[DEBUG] agent_status_info has {len(agent_status_info)} entries: {agent_status_info}")

            # Render the base template
            rendered_prompt = template.render(**template_vars)

            # Add agent status information to the end of the prompt if available
            # (suppressed when communication / other-agent visibility is cut)
            if agent_states and len(agent_states) > 1 and not comms_off:
                agent_status_info = template_vars.get('agent_status_info', [])
                if agent_status_info:
                    status_lines = ["\n\n=== PARTY AGENT STATUS ==="]
                    for agent_info in agent_status_info:
                        username = agent_info.get('username', 'unknown')
                        status = agent_info.get('status', 'unknown')
                        hp = agent_info.get('hp')
                        max_hp = agent_info.get('max_hp')
                        mp = agent_info.get('mp')
                        max_mp = agent_info.get('max_mp')

                        # Determine if agent is offline/dead
                        if hp is not None and hp == 0:
                            status_display = "offline"
                        elif status == 'idle':
                            status_display = "offline"
                        else:
                            status_display = status

                        # Build status line
                        status_line = f"- {username}: {status_display}"
                        if hp is not None and max_hp is not None:
                            status_line += f" | HP: {hp}/{max_hp}"
                            if hp == 0:
                                status_line += " (DEAD)"
                        if mp is not None and max_mp is not None:
                            status_line += f" | MP: {mp}/{max_mp}"

                        status_lines.append(status_line)

                    status_lines.append("=== END PARTY STATUS ===")
                    rendered_prompt += "\n".join(status_lines)

            rendered_prompt += self._experiment_prompt_suffix(task_config, resolved_max_rounds)
            return rendered_prompt
        else:
            # Fallback to original format if no template is defined
            prompt_parts = [
                f"Task: {task_config.name}",
                f"Description: {task_config.description}",
                f"Primary Objective: {task_config.objectives['primary']}"
            ]
            
            if 'secondary' in task_config.objectives:
                prompt_parts.append("Secondary Objectives:")
                for obj in task_config.objectives['secondary']:
                    prompt_parts.append(f"- {obj}")
            
            if relevant_context:
                prompt_parts.extend([
                    "",
                    "Relevant Context:",
                    relevant_context
                ])
            
            if task_config.success_criteria:
                prompt_parts.extend([
                    "",
                    "Success Criteria:"
                ])
                for criteria in task_config.success_criteria:
                    prompt_parts.append(f"- {criteria}")
            
            suffix = self._experiment_prompt_suffix(task_config, resolved_max_rounds)
            return "\\n".join(prompt_parts) + suffix

    def _experiment_prompt_suffix(self, task_config: TaskConfig, resolved_max_rounds: int) -> str:
        """Build the trailing experiment directives appended to every task prompt.

        Covers the round budget, the --no-roles directive, the no-communication notice,
        and the --shared-plan-only injected plan. Returns '' when nothing applies.
        """
        exp = self.experiment
        parts: List[str] = []

        # Always communicate the real (resolved) round budget so it overrides any
        # hardcoded number baked into the agent system prompt.
        parts.append(
            f"\n\n=== ROUND BUDGET ===\nYour team has a MAXIMUM of {resolved_max_rounds} rounds "
            f"to complete the task. Work efficiently.\n=== END ROUND BUDGET ==="
        )

        if exp.no_roles:
            parts.append(
                "\n\n=== ROLE ASSIGNMENT ===\nRoles are NOT pre-assigned. Do not infer your job "
                "from your name or anyone else's. The team must self-organize and decide who does "
                "what based on the current situation.\n=== END ROLE ASSIGNMENT ==="
            )

        if exp.single_agent_upper_bound:
            parts.append(
                "\n\n=== SOLO UPPER BOUND ===\nYou are the ONLY agent participating in this run. "
                "No other agents are spawned, there is no discussion phase, and communication "
                "tools are disabled. You must complete every part of the task yourself. "
                "Ignore any task text that says to coordinate, discuss, transfer to teammates, "
                "or wait for other agents.\n=== END SOLO UPPER BOUND ==="
            )

        if exp.no_communication:
            parts.append(
                "\n\n=== NO COMMUNICATION ===\nYou cannot communicate with other agents (no chat, "
                "no item transfers, and other agents are not visible to you). Act independently "
                "using only the information you can directly observe.\n=== END NO COMMUNICATION ==="
            )

        if exp.shared_plan_only:
            plan = task_config.shared_plan or task_config.relevant_game_context or "(no shared plan provided)"
            parts.append(
                "\n\n=== SHARED PLAN (read-only) ===\nThe team agreed on this plan in advance. "
                "You cannot communicate further; execute your part of it independently.\n"
                f"{plan}\n=== END SHARED PLAN ==="
            )

        return "".join(parts)
    
    def _init_trajectory(self, task_path: str, task_config: TaskConfig):
        """Initialize trajectory data structure"""
        # Extract task number from path
        task_filename = Path(task_path).stem
        task_number = task_filename.split('_')[1] if '_' in task_filename else task_filename
        
        # Load the complete task definition from file
        with open(task_path, 'r') as f:
            task_definition = yaml.safe_load(f)
        
        self.trajectory_data = {
            'task_id': f"task_{task_number}",
            'timestamp': datetime.now().isoformat(),
            'task_definition': task_definition,
            'rounds': [],
            'metrics': {}
        }

    def _save_task_summary(self, task_config: TaskConfig, results: Dict[str, Any]):
        """Save task execution summary"""
        summary_file = self.output_dir / f"task_summary_{self.run_timestamp}.json"
        
        summary = {
            'task': {
                'name': task_config.name,
                'description': task_config.description,
                'objectives': task_config.objectives,
                'success_criteria': task_config.success_criteria
            },
            'execution': {
                'timestamp': datetime.now().isoformat(),
                'agent_config': self.agent_config_path,
                'results': results
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"📄 Task summary saved to: {summary_file}")
        
        # Save trajectory file
        self._save_trajectory(task_config, results)

    def _collect_action_data(self, agent_name: str, agent_state: AgentExecutionState, response: str) -> Dict[str, Any]:
        """Collect trajectory data for a single agent action"""
        import re

        # Get agent status
        status = self._get_agent_status_details(agent_state)

        # Extract tool call information
        tool_call_info = ""
        tool_result = ""

        # Extract TOOL_CALL_INFO
        tool_call_match = re.search(r'\[TOOL_CALL_INFO\] ([^\n]+)', response)
        if tool_call_match:
            tool_call_info = tool_call_match.group(1)

        # Extract TOOL_RESULT
        tool_result_match = re.search(r'\[TOOL_RESULT\] ([^\n]+)', response)
        if tool_result_match:
            tool_result = tool_result_match.group(1)

        # Get observation data if available
        observation_data = None
        try:
            if agent_state.console and agent_state.console.agent.game_tools:
                observation_data = agent_state.console.agent.game_tools.get_last_observation_data()
        except Exception as e:
            self.logger.debug(f"Failed to get observation for {agent_name}: {e}")

        return {
            'agent_name': agent_name,
            'status': status,
            'action': tool_call_info,
            'observation': observation_data if observation_data else '',
            'thinking': '',
        }

    def _save_trajectory(self, task_config: TaskConfig, results: Dict[str, Any]):
        """Save trajectory data to JSON file"""
        # Extract task number from task_id
        task_number = self.trajectory_data['task_id'].split('_')[1] if '_' in self.trajectory_data['task_id'] else self.trajectory_data['task_id']
        trajectory_file = self.output_dir / f"task_{task_number}_trajectory.json"
        
        # Update metrics from results
        if '_multi_agent_metrics' in results:
            self.trajectory_data['metrics'] = results['_multi_agent_metrics']
        
        with open(trajectory_file, 'w') as f:
            json.dump(self.trajectory_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Trajectory saved to: {trajectory_file}")

    def _check_task_success_early(self) -> Tuple[bool, str]:
        """
        Check if the task has been completed successfully using the Python verifier.
        This enables early stopping to save tokens and time.

        Returns:
            Tuple[bool, str]: (success, message) where success is True if task is complete
        """
        try:
            # Get task number from trajectory data
            task_id = self.trajectory_data.get('task_id', '')
            if not task_id:
                return False, "No task_id in trajectory data"

            # Extract task number (e.g., "task_01" -> "01")
            import re
            match = re.search(r'task_(\d+)', task_id)
            if not match:
                return False, f"Could not parse task number from {task_id}"

            task_num = int(match.group(1))

            # Try to import the verifier module
            verifier_path = Path(__file__).parent.parent / "data_v0.1_multi" / "v1.3_benchmark"
            verifier_file = verifier_path / f"task_{task_num:02d}_success_criteria.py"

            if not verifier_file.exists():
                self.logger.debug(f"No verifier found at {verifier_file}")
                return False, f"No verifier for task {task_num:02d}"

            # Dynamically import the verifier module
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"task_{task_num:02d}_verifier", verifier_file)
            verifier_module = importlib.util.module_from_spec(spec)

            # Add verifier_utils to the module's namespace
            verifier_utils_path = verifier_path / "verifier_utils.py"
            if verifier_utils_path.exists():
                utils_spec = importlib.util.spec_from_file_location("verifier_utils", verifier_utils_path)
                utils_module = importlib.util.module_from_spec(utils_spec)
                sys.modules['verifier_utils'] = utils_module
                utils_spec.loader.exec_module(utils_module)

            spec.loader.exec_module(verifier_module)

            # Call the verify function
            if hasattr(verifier_module, 'verify'):
                success, msg = verifier_module.verify(self.trajectory_data)
                return bool(success), msg
            else:
                return False, "Verifier module has no verify() function"

        except Exception as e:
            self.logger.debug(f"Early success check failed: {e}")
            return False, f"Verification error: {str(e)}"

    def _save_folder_summary(self, folder_path: str, all_results: Dict[str, Any]):
        """Save folder execution summary"""
        summary_file = self.output_dir / f"folder_summary_{self.run_timestamp}.json"
        
        summary = {
            'folder': folder_path,
            'execution': {
                'timestamp': datetime.now().isoformat(),
                'agent_config': self.agent_config_path,
                'total_tasks': len(all_results),
                'results': all_results
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"📄 Folder summary saved to: {summary_file}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AgentWorld Task Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single task
  python run.py --task data_v0.1_solo/task_1.yaml --agent configs/qwen_agent.yaml --output logs/

  # Run all tasks in folder
  python run.py --task-folder data_v0.1_solo/ --agent configs/qwen_agent.yaml --output logs/

  # Run with different agent configuration
  python run.py --task task.yaml --agent configs/openai_agent.yaml --output results/
        """
    )
    
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument(
        "--task",
        type=str,
        help="Path to single task YAML file"
    )
    task_group.add_argument(
        "--task-folder",
        type=str,
        help="Path to folder containing task YAML files"
    )
    
    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        help="Path to agent configuration YAML file"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output directory for logs and results"
    )
    
    parser.add_argument(
        "--no-split-screen",
        action="store_true",
        help="Disable split-screen interface and use regular console output"
    )
    
    parser.add_argument(
        "--dump-prompts",
        action="store_true",
        help="Dump prompt messages when calling LLM into /tmp/prompts folder"
    )

    # ===== Experiment baselines =====
    exp = parser.add_argument_group("experiment baselines")
    exp.add_argument(
        "--single-agent-upper-bound",
        action="store_true",
        help="Collapse a multi-agent task into ONE agent with merged abilities (max skills, summed inventory, unioned equipment)."
    )
    exp.add_argument(
        "--discussion-rounds",
        type=int,
        default=0,
        metavar="N",
        help="First N rounds are chat-only (all other actions disabled); communication is fully cut afterwards."
    )
    exp.add_argument(
        "--no-communication",
        action="store_true",
        help="Cut communication from round 1 (no chat tool, no transfers, no chat history, other agents hidden)."
    )
    exp.add_argument(
        "--shared-plan-only",
        action="store_true",
        help="Cut communication but inject a single shared plan (task YAML 'shared_plan' or relevant_game_context) into every agent prompt."
    )
    exp.add_argument(
        "--random-agent",
        action="store_true",
        help="Skip the LLM entirely; each turn take a uniformly random legal action."
    )

    # ===== Design knobs (combinable with any baseline) =====
    knobs = parser.add_argument_group("experiment design knobs")
    knobs.add_argument(
        "--max-rounds",
        type=int,
        default=None,
        metavar="N",
        help=f"Override the round budget. Precedence: this flag > task YAML 'rounds' > {DEFAULT_MAX_ROUNDS}."
    )
    knobs.add_argument(
        "--no-roles",
        action="store_true",
        help="Present a generic identity and a 'roles are not pre-assigned, self-organize' directive (prompt-only)."
    )
    knobs.add_argument(
        "--random-spawn",
        action="store_true",
        help="Replace each agent's configured spawn location with a seeded random coordinate."
    )
    knobs.add_argument(
        "--spawn-region",
        type=int,
        nargs=4,
        default=None,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Bounding box for --random-spawn (requires --random-spawn)."
    )
    knobs.add_argument(
        "--no-task-docs",
        action="store_true",
        help="Drop the task-specific document (relevant_game_context) from the prompt."
    )
    knobs.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="N",
        help="Seed RNG for --random-spawn and --random-agent (reproducibility)."
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Validate inputs
    if args.task and not os.path.exists(args.task):
        print(f"❌ Error: Task file not found: {args.task}")
        sys.exit(1)
    
    if args.task_folder and not os.path.exists(args.task_folder):
        print(f"❌ Error: Task folder not found: {args.task_folder}")
        sys.exit(1)
    
    if not os.path.exists(args.agent):
        print(f"❌ Error: Agent config file not found: {args.agent}")
        sys.exit(1)
    
    # Build and validate experiment configuration from baseline flags
    try:
        experiment = ExperimentConfig.from_args(args)
        experiment.validate()
    except ValueError as e:
        print(f"❌ Error: invalid experiment configuration: {e}")
        sys.exit(1)

    try:
        # Clear /tmp/prompts folder if dump-prompts is enabled
        if args.dump_prompts:
            import shutil
            prompts_dir = "/tmp/prompts"
            if os.path.exists(prompts_dir):
                shutil.rmtree(prompts_dir)
                print(f"🗑️ Cleared existing prompts folder: {prompts_dir}")
            os.makedirs(prompts_dir, exist_ok=True)
            print(f"📁 Created prompts dump folder: {prompts_dir}")
        
        # Create task runner
        use_split_screen = not args.no_split_screen
        runner = TaskRunner(args.agent, args.output, use_split_screen, args.dump_prompts, experiment)
        
        # Execute tasks
        if args.task:
            print(f"🚀 Running single task: {args.task}")
            results = runner.run_single_task(args.task)
        else:
            print(f"🚀 Running all tasks in folder: {args.task_folder}")
            results = runner.run_task_folder(args.task_folder)
        
        # Print summary
        print("\\n" + "="*80)
        print("📊 EXECUTION SUMMARY")
        print("="*80)
        
        if args.task:
            # Single task summary
            for agent_name, result in results.items():
                # Skip metrics that aren't actual agent results
                if agent_name == '_multi_agent_metrics':
                    continue
                status = "✅ SUCCESS" if result.get('success', False) else "❌ FAILED"
                print(f"Agent {agent_name}: {status}")
                if 'duration_seconds' in result:
                    print(f"  Duration: {result['duration_seconds']:.2f}s")
                if 'iterations' in result:
                    print(f"  Iterations: {result['iterations']}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
        else:
            # Folder summary
            total_tasks = len(results)
            successful_tasks = sum(1 for task_results in results.values() 
                                 if not isinstance(task_results, dict) or 'error' not in task_results)
            
            print(f"Total tasks: {total_tasks}")
            print(f"Successful: {successful_tasks}")
            print(f"Failed: {total_tasks - successful_tasks}")
        
        print(f"\\n📁 Results saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
