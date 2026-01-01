"""
Beam Search Verification Module

Main orchestration for beam search-based task verification.
Optimized with parallel API calls and Claude inference.
"""

import copy
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .task_loader import load_task, task_to_initial_states, get_task_context, TaskConfig
from .simulation_client import SimulationClient, SimulationResult
from .action_proposer import propose_actions
from .verifier_adapter import states_to_trajectory, verify_task, quick_verify_state
from .branch_evaluator import select_best_branches

# Number of parallel workers for different operations
API_WORKERS = 8      # For simulation API calls (fast)
CLAUDE_WORKERS = 8   # For Claude CLI calls (using Haiku for speed)


@dataclass
class BranchState:
    """Represents a single branch in the beam search."""
    agent_states: Dict[str, Dict[str, Any]]
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    step_count: int = 0
    observations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_actions: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> 'BranchState':
        """Create a deep copy of this branch."""
        return BranchState(
            agent_states=copy.deepcopy(self.agent_states),
            action_history=copy.deepcopy(self.action_history),
            step_count=self.step_count,
            observations=copy.deepcopy(self.observations),
            last_actions=copy.deepcopy(self.last_actions)
        )


@dataclass
class VerificationResult:
    """Result of verification run."""
    success: bool
    steps_taken: int
    final_states: Dict[str, Dict[str, Any]]
    action_history: List[Dict[str, Any]]
    verifier_message: str
    elapsed_time: float = 0.0
    task_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'steps_taken': self.steps_taken,
            'final_states': self.final_states,
            'action_history': self.action_history,
            'verifier_message': self.verifier_message,
            'elapsed_time': self.elapsed_time,
            'task_id': self.task_id
        }


class BeamSearchVerifier:
    """
    Beam search-based task verification.

    Uses Claude to propose actions, simulates them, and verifies success.
    """

    def __init__(
        self,
        task_path: str,
        beam_size: int = 2,
        max_steps: int = 25,
        api_base: str = "http://localhost:7031",
        verbose: bool = True
    ):
        """
        Initialize the verifier.

        Args:
            task_path: Path to task YAML file
            beam_size: Number of beams to maintain
            max_steps: Maximum steps before giving up
            api_base: Base URL for simulation API
            verbose: Whether to print progress
        """
        self.task = load_task(task_path)
        self.task_context = get_task_context(self.task)
        self.beam_size = beam_size
        self.max_steps = min(max_steps, self.task.max_action_steps)
        self.sim_client = SimulationClient(api_base)
        self.verbose = verbose

    def log(self, message: str):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)

    def get_observations(self, agent_states: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get observations for all agents in parallel."""
        observations = {}

        def fetch_observation(agent_name: str, state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
            obs = self.sim_client.observe(state['x'], state['y'], radius=15)
            return agent_name, obs

        with ThreadPoolExecutor(max_workers=API_WORKERS) as executor:
            futures = {
                executor.submit(fetch_observation, name, state): name
                for name, state in agent_states.items()
            }
            for future in as_completed(futures):
                agent_name, obs = future.result()
                observations[agent_name] = obs

        return observations

    def execute_action_set(
        self,
        agent_states: Dict[str, Dict[str, Any]],
        action_set: Dict[str, Dict[str, Any]]
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
        """
        Execute a set of actions for all agents in parallel.

        Args:
            agent_states: Current states for all agents
            action_set: Actions for each agent {agent_name: action}

        Returns:
            Tuple of (new_states, action_results)
        """
        new_states = {}
        action_results = {}

        # Separate wait actions (no API call needed) from real actions
        wait_actions = {}
        api_actions = {}

        for agent_name, action in action_set.items():
            if agent_name not in agent_states:
                continue

            if action.get('type') == 'wait':
                wait_actions[agent_name] = action
            else:
                api_actions[agent_name] = action

        # Handle wait actions immediately (no API call)
        for agent_name, action in wait_actions.items():
            current_state = agent_states[agent_name]
            new_states[agent_name] = copy.deepcopy(current_state)
            action_results[agent_name] = {
                'action': action,
                'success': True,
                'message': 'Waiting',
                'state_after': current_state
            }

        # Execute real actions in parallel
        def execute_single_action(agent_name: str, action: Dict[str, Any]) -> Tuple[str, Dict[str, Any], SimulationResult]:
            current_state = agent_states[agent_name]
            result = self.sim_client.act(current_state, action)
            return agent_name, action, result

        if api_actions:
            with ThreadPoolExecutor(max_workers=API_WORKERS) as executor:
                futures = {
                    executor.submit(execute_single_action, name, action): name
                    for name, action in api_actions.items()
                }
                for future in as_completed(futures):
                    agent_name, action, result = future.result()
                    new_states[agent_name] = result.state_after
                    action_results[agent_name] = {
                        'action': action,
                        'success': result.success,
                        'message': result.message,
                        'state_after': result.state_after
                    }

        return new_states, action_results

    def run(self) -> VerificationResult:
        """
        Run beam search verification.

        Returns:
            VerificationResult with success status and details
        """
        start_time = time.time()

        # Initialize
        self.log(f"Starting verification for: {self.task.name}")
        self.log(f"Task ID: {self.task.task_id}")
        self.log(f"Agents: {list(self.task.agents.keys())}")
        self.log(f"Max steps: {self.max_steps}, Beam size: {self.beam_size}")
        self.log("-" * 60)

        # Check API health
        if not self.sim_client.health_check():
            return VerificationResult(
                success=False,
                steps_taken=0,
                final_states={},
                action_history=[],
                verifier_message="API server not reachable",
                elapsed_time=time.time() - start_time,
                task_id=self.task.task_id
            )

        # Get initial states
        initial_states = task_to_initial_states(self.task)

        # Validate and adjust starting positions if blocked
        self.log("Validating starting positions...")
        for agent_name, state in initial_states.items():
            orig_x, orig_y = state['x'], state['y']
            new_x, new_y = self.sim_client.find_walkable_position(orig_x, orig_y, max_radius=30)
            if (new_x, new_y) != (orig_x, orig_y):
                self.log(f"  {agent_name}: ({orig_x},{orig_y}) blocked, moved to ({new_x},{new_y})")
                state['x'] = new_x
                state['y'] = new_y
            else:
                self.log(f"  {agent_name}: ({orig_x},{orig_y}) OK")

        # Group agents together if they were scattered by position adjustment
        # Find a common walkable area for all agents
        positions = [(s['x'], s['y']) for s in initial_states.values()]
        if len(set(positions)) > 1:  # Agents are at different positions
            # Use the first agent's position as base and group others nearby
            base_x, base_y = positions[0]
            offset = 0
            for agent_name, state in initial_states.items():
                state['x'] = base_x + offset
                state['y'] = base_y
                offset += 1
            self.log(f"  Grouped agents near ({base_x},{base_y})")

        # Create initial branch
        initial_branch = BranchState(
            agent_states=initial_states,
            action_history=[],
            step_count=0
        )

        # Get initial observations
        initial_branch.observations = self.get_observations(initial_states)

        # Maintain list of active branches
        branches = [initial_branch]

        # Main beam search loop
        for step in range(self.max_steps):
            self.log(f"\n=== Step {step + 1}/{self.max_steps} ===")
            self.log(f"Active branches: {len(branches)}")

            # PHASE 1: Get observations for all branches in parallel
            self.log("Getting observations for all branches...")
            for branch in branches:
                branch.observations = self.get_observations(branch.agent_states)

            # PHASE 2: Propose actions for all branches in parallel (Claude CLI calls)
            self.log("Proposing actions for all branches in parallel...")

            def propose_for_branch(branch_idx: int, branch: BranchState) -> Tuple[int, List[Dict[str, Dict[str, Any]]]]:
                """Call propose_actions for a single branch."""
                action_sets = propose_actions(
                    self.task_context,
                    branch.agent_states,
                    branch.observations,
                    branch.action_history,
                    beam_count=self.beam_size
                )
                return branch_idx, action_sets

            branch_action_sets = {}
            with ThreadPoolExecutor(max_workers=CLAUDE_WORKERS) as executor:
                futures = {
                    executor.submit(propose_for_branch, idx, branch): idx
                    for idx, branch in enumerate(branches)
                }
                for future in as_completed(futures):
                    branch_idx, action_sets = future.result()
                    branch_action_sets[branch_idx] = action_sets
                    self.log(f"  Branch {branch_idx + 1}: got {len(action_sets)} action sets")

            # PHASE 3: Execute all action sets and create new branches
            new_branches = []
            verifier_results = []
            pending_executions = []  # (branch, action_set, branch_idx, action_idx)

            for branch_idx, branch in enumerate(branches):
                action_sets = branch_action_sets.get(branch_idx, [])
                self.log(f"\nBranch {branch_idx + 1}:")
                for action_idx, action_set in enumerate(action_sets):
                    self.log(f"  Action set {action_idx + 1}:")
                    for agent, action in action_set.items():
                        self.log(f"    {agent}: {action.get('type', 'unknown')}")
                    pending_executions.append((branch, action_set, branch_idx, action_idx))

            # Execute all action sets in parallel
            def execute_and_verify(args: Tuple) -> Tuple[BranchState, Tuple[bool, str], int, int]:
                """Execute action set and verify result."""
                branch, action_set, branch_idx, action_idx = args
                new_branch = branch.clone()
                new_states, action_results = self.execute_action_set(
                    new_branch.agent_states,
                    action_set
                )
                new_branch.agent_states = new_states
                new_branch.last_actions = action_results
                new_branch.action_history.append(action_results)
                new_branch.step_count += 1

                # Verify this branch
                success, message = quick_verify_state(
                    self.task.task_id,
                    new_branch.agent_states,
                    new_branch.action_history
                )
                return new_branch, (success, message), branch_idx, action_idx

            if pending_executions:
                with ThreadPoolExecutor(max_workers=API_WORKERS) as executor:
                    futures = [executor.submit(execute_and_verify, args) for args in pending_executions]
                    for future in as_completed(futures):
                        new_branch, verify_result, branch_idx, action_idx = future.result()
                        success, message = verify_result

                        # Log results
                        self.log(f"  Branch {branch_idx + 1}, Action {action_idx + 1} results:")
                        for agent, result in new_branch.last_actions.items():
                            status = "✓" if result['success'] else "✗"
                            self.log(f"    {agent}: {status} {result['message'][:40]}")

                        new_branches.append(new_branch)
                        verifier_results.append((success, message))

                        # Early exit if succeeded
                        if success:
                            self.log(f"\n SUCCESS! Task completed in {new_branch.step_count} steps")
                            return VerificationResult(
                                success=True,
                                steps_taken=new_branch.step_count,
                                final_states=new_branch.agent_states,
                                action_history=new_branch.action_history,
                                verifier_message=message,
                                elapsed_time=time.time() - start_time,
                                task_id=self.task.task_id
                            )

            # Select best branches to keep
            if len(new_branches) > self.beam_size:
                self.log(f"\nPruning {len(new_branches)} branches to {self.beam_size}...")

                # Convert to format for evaluator
                branch_data = [
                    {
                        'agent_states': b.agent_states,
                        'last_actions': b.last_actions,
                        'step_count': b.step_count
                    }
                    for b in new_branches
                ]

                selected_indices = select_best_branches(
                    branch_data,
                    verifier_results,
                    self.task_context,
                    max_branches=self.beam_size,
                    use_claude=True
                )

                branches = [new_branches[i] for i in selected_indices]
                self.log(f"Kept branches: {[i+1 for i in selected_indices]}")
            else:
                branches = new_branches

            # Log current state summary
            for branch_idx, branch in enumerate(branches):
                self.log(f"\nBranch {branch_idx + 1} status:")
                for agent, state in branch.agent_states.items():
                    inv_count = sum(1 for i in state.get('inventory', []) if i)
                    self.log(f"  {agent}: pos=({state['x']},{state['y']}), "
                            f"hp={state['hitPoints']}/{state['maxHitPoints']}, "
                            f"items={inv_count}")

        # Max steps reached
        best_branch = branches[0] if branches else initial_branch

        # Final verification
        success, message = quick_verify_state(
            self.task.task_id,
            best_branch.agent_states,
            best_branch.action_history
        )

        self.log(f"\n=== FAILED: Max steps ({self.max_steps}) reached ===")
        self.log(f"Verifier message: {message}")

        return VerificationResult(
            success=success,
            steps_taken=best_branch.step_count,
            final_states=best_branch.agent_states,
            action_history=best_branch.action_history,
            verifier_message=message,
            elapsed_time=time.time() - start_time,
            task_id=self.task.task_id
        )


def run_single_task(
    task_path: str,
    beam_size: int = 2,
    max_steps: int = 25,
    api_base: str = "http://localhost:7031",
    verbose: bool = True
) -> VerificationResult:
    """
    Run verification on a single task.

    Args:
        task_path: Path to task YAML
        beam_size: Beam size for search
        max_steps: Maximum steps
        api_base: API base URL
        verbose: Print progress

    Returns:
        VerificationResult
    """
    verifier = BeamSearchVerifier(
        task_path=task_path,
        beam_size=beam_size,
        max_steps=max_steps,
        api_base=api_base,
        verbose=verbose
    )
    return verifier.run()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m beam_verifier.beam_search <task_yaml_path>")
        sys.exit(1)

    task_path = sys.argv[1]
    result = run_single_task(task_path)

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(json.dumps(result.to_dict(), indent=2, default=str))
