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
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import existing agent components
from agent_factory import AgentFactory
from console import GameConsole
from base_agent import BaseAgent


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
            # Use custom system prompt template
            base_prompt = self.custom_system_prompt
            
            # Get current environment observation and append it to the system prompt
            current_observation = self.base_agent._get_current_environment_observation()
            if current_observation:
                # Replace the {{observation}} placeholder with actual observation
                if "{{observation}}" in base_prompt:
                    base_prompt = base_prompt.replace("{{observation}}", current_observation)
                else:
                    # Fallback: append observation if placeholder not found
                    base_prompt += f"\n\n=== CURRENT ENVIRONMENT OBSERVATION ===\n{current_observation}\n=== END OBSERVATION ==="
            else:
                # Remove the observation placeholder if no observation available
                base_prompt = base_prompt.replace("{{observation}}", "No observation data available")
            
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


@dataclass
class AgentConfig:
    """Agent configuration data structure"""
    name: str
    provider: str
    llm: Dict[str, Any]
    game: Dict[str, Any]
    system_prompt: Optional[str] = None


class TaskRunner:
    """Main task runner class"""
    
    def __init__(self, agent_config_path: str, output_dir: str):
        """Initialize the task runner"""
        self.agent_config_path = agent_config_path
        
        # Create a unique run folder for this execution
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_output_dir = Path(output_dir)
        self.output_dir = self.base_output_dir / f"run_{self.run_timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load agent configuration
        self.agent_config = self._load_agent_config()
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f"TaskRunner initialized with agent config: {agent_config_path}")
        self.logger.info(f"Run folder created: {self.output_dir}")
        self.logger.info(f"Run timestamp: {self.run_timestamp}")
    
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
                system_prompt=agent_data.get('system_prompt')
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
                relevant_game_context=config_data.get('relevant_game_context')
            )
        except Exception as e:
            self.logger.error(f"Error loading task config from {task_path}: {e}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.output_dir / f"task_runner_{self.run_timestamp}.log"
        
        # Create logger
        self.logger = logging.getLogger('TaskRunner')
        self.logger.setLevel(logging.INFO)  # Default to INFO level
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _create_agent_console(self, agent_name: str, agent_data: Dict[str, Any]) -> GameConsole:
        """Create a GameConsole instance for the agent"""
        
        # Parse location
        location = None
        if 'location' in agent_data:
            location = (agent_data['location']['x'], agent_data['location']['y'])
        
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
            new_character=agent_data.get('new_character', False)
        )
        
        # Override agent with configurable system prompt if provided
        if self.agent_config.system_prompt:
            console.agent = ConfigurableAgent(console.agent, self.agent_config.system_prompt)
        
        # Override max iterations (default to 50 if not in config)
        console.max_iterations = 50
        
        return console
    
    def run_single_task(self, task_path: str) -> Dict[str, Any]:
        """Run a single task from configuration file"""
        self.logger.info(f"🎯 Starting task: {task_path}")
        
        # Load task configuration
        task_config = self._load_task_config(task_path)
        
        self.logger.info(f"Task: {task_config.name}")
        self.logger.info(f"Description: {task_config.description}")
        self.logger.info(f"Primary objective: {task_config.objectives['primary']}")
        
        results = {}
        
        # Execute task for each agent
        for agent_name, agent_data in task_config.agents.items():
            self.logger.info(f"🤖 Running task with agent: {agent_name}")
            
            try:
                # Create agent console
                console = self._create_agent_console(agent_name, agent_data)
                
                # Build task prompt from configuration
                task_prompt = self._build_task_prompt(task_config)
                
                # Execute the task
                start_time = time.time()
                
                self.logger.info(f"Executing task: {task_prompt}")
                
                # Auto-login first
                try:
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
        
        all_results = {}
        
        for task_file in sorted(task_files):
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
    
    def _build_task_prompt(self, task_config: TaskConfig) -> str:
        """Build task prompt from configuration"""
        prompt_parts = [
            f"Task: {task_config.name}",
            f"Description: {task_config.description}",
            f"Primary Objective: {task_config.objectives['primary']}"
        ]
        
        if 'secondary' in task_config.objectives:
            prompt_parts.append("Secondary Objectives:")
            for obj in task_config.objectives['secondary']:
                prompt_parts.append(f"- {obj}")
        
        if task_config.relevant_game_context:
            prompt_parts.extend([
                "",
                "Relevant Context:",
                task_config.relevant_game_context
            ])
        
        if task_config.success_criteria:
            prompt_parts.extend([
                "",
                "Success Criteria:"
            ])
            for criteria in task_config.success_criteria:
                prompt_parts.append(f"- {criteria}")
        
        return "\\n".join(prompt_parts)
    
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
    
    try:
        # Create task runner
        runner = TaskRunner(args.agent, args.output)
        
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
