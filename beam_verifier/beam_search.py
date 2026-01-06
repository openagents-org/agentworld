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
from .action_proposer import propose_actions, propose_actions_multi_branch, summarize_team_inventory
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
        actions_per_branch: int = 5,
        max_steps: int = 25,
        api_base: str = "http://localhost:7031",
        verbose: bool = True
    ):
        """
        Initialize the verifier.

        Args:
            task_path: Path to task YAML file
            beam_size: Number of beams to maintain after pruning
            actions_per_branch: Number of action sets to propose per branch
            max_steps: Maximum steps before giving up
            api_base: Base URL for simulation API
            verbose: Whether to print progress
        """
        self.task = load_task(task_path)
        self.task_context = get_task_context(self.task)
        self.beam_size = beam_size
        self.actions_per_branch = actions_per_branch
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

        # Separate different action types
        wait_actions = {}
        transfer_actions = {}
        equip_actions = {}
        api_actions = {}

        for agent_name, action in action_set.items():
            if agent_name not in agent_states:
                continue

            action_type = action.get('type')
            if action_type == 'wait':
                wait_actions[agent_name] = action
            elif action_type == 'transfer':
                transfer_actions[agent_name] = action
            elif action_type == 'equip':
                equip_actions[agent_name] = action
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

        # Handle transfer actions locally (modify both sender and receiver states)
        # First, initialize new_states for all agents involved in transfers
        for agent_name in transfer_actions:
            if agent_name not in new_states:
                new_states[agent_name] = copy.deepcopy(agent_states[agent_name])

        for agent_name, action in transfer_actions.items():
            target_player = action.get('targetPlayer', '')
            item_key = action.get('itemKey', '')
            count = action.get('count', 1)

            # Ensure target exists in new_states
            if target_player in agent_states and target_player not in new_states:
                new_states[target_player] = copy.deepcopy(agent_states[target_player])

            # Execute local transfer
            success, message = self._execute_local_transfer(
                new_states, agent_name, target_player, item_key, count
            )

            action_results[agent_name] = {
                'action': action,
                'success': success,
                'message': message,
                'state_after': new_states.get(agent_name, agent_states.get(agent_name, {}))
            }

        # Handle equip actions locally (to support items the API doesn't recognize)
        for agent_name, action in equip_actions.items():
            if agent_name not in new_states:
                new_states[agent_name] = copy.deepcopy(agent_states[agent_name])

            inventory_index = action.get('inventoryIndex', 0)
            success, message = self._execute_local_equip(
                new_states[agent_name], inventory_index
            )

            action_results[agent_name] = {
                'action': action,
                'success': success,
                'message': message,
                'state_after': new_states[agent_name]
            }

        # Execute real actions in parallel
        def sanitize_action(action: Dict[str, Any]) -> Dict[str, Any]:
            """Ensure action parameters are valid types."""
            action = action.copy()
            action_type = action.get('type', '')

            # Fix common errors: wrong skill for arrows
            if action_type == 'craft':
                item_key = action.get('itemKey', '').lower()
                # Fix plural "arrows" to singular "arrow"
                if item_key == 'arrows':
                    action['itemKey'] = 'arrow'
                    item_key = 'arrow'
                if item_key == 'arrow':
                    # Arrows MUST use Fletching skill
                    action['skill'] = 'Fletching'
                    # Set count=1 for arrows - game crafts 1 batch = 10 arrows (10 sticks + 10 feathers)
                    action['count'] = 1
                    return action

            # Ensure count is a valid integer for craft/transfer actions (except arrows)
            if action_type in ('craft', 'transfer') or 'count' in action:
                count = action.get('count')
                if count is None or (isinstance(count, float) and str(count) == 'nan'):
                    action['count'] = 1
                else:
                    try:
                        action['count'] = int(count)
                    except (ValueError, TypeError):
                        action['count'] = 1
            return action

        def execute_single_action(agent_name: str, action: Dict[str, Any]) -> Tuple[str, Dict[str, Any], SimulationResult]:
            current_state = agent_states[agent_name]
            action = sanitize_action(action)
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

    def _execute_local_transfer(
        self,
        states: Dict[str, Dict[str, Any]],
        sender: str,
        receiver: str,
        item_key: str,
        count: int
    ) -> Tuple[bool, str]:
        """
        Execute a local item transfer between two agents.

        Modifies states in-place.

        Args:
            states: Dict of agent states (will be modified)
            sender: Name of agent sending items
            receiver: Name of agent receiving items
            item_key: Key of item to transfer
            count: Number of items to transfer

        Returns:
            Tuple of (success, message)
        """
        # Validate agents exist
        if sender not in states:
            return False, f"Sender '{sender}' not found"
        if receiver not in states:
            return False, f"Receiver '{receiver}' not found"

        sender_state = states[sender]
        receiver_state = states[receiver]

        sender_inventory = sender_state.get('inventory', [])
        receiver_inventory = receiver_state.get('inventory', [])

        # Find item in sender's inventory
        sender_slot = None
        sender_item = None
        for i, item in enumerate(sender_inventory):
            if item and isinstance(item, dict) and item.get('key', '').lower() == item_key.lower():
                sender_slot = i
                sender_item = item
                break

        if sender_slot is None:
            return False, f"Item '{item_key}' not found in {sender}'s inventory"

        available_count = sender_item.get('count', 1)
        if available_count < count:
            return False, f"Not enough {item_key}: have {available_count}, need {count}"

        # Find empty slot in receiver's inventory, or existing stack of same item
        receiver_slot = None
        for i, item in enumerate(receiver_inventory):
            if item and isinstance(item, dict) and item.get('key', '').lower() == item_key.lower():
                # Found existing stack
                receiver_slot = i
                break

        if receiver_slot is None:
            # Find empty slot
            for i, item in enumerate(receiver_inventory):
                if item is None:
                    receiver_slot = i
                    break

        if receiver_slot is None:
            return False, f"{receiver}'s inventory is full"

        # Execute the transfer
        # Remove from sender
        if available_count == count:
            sender_inventory[sender_slot] = None
        else:
            sender_inventory[sender_slot] = {
                'key': sender_item.get('key'),
                'count': available_count - count
            }

        # Add to receiver
        existing_item = receiver_inventory[receiver_slot]
        if existing_item and isinstance(existing_item, dict):
            # Add to existing stack
            receiver_inventory[receiver_slot] = {
                'key': existing_item.get('key'),
                'count': existing_item.get('count', 1) + count
            }
        else:
            # New stack
            receiver_inventory[receiver_slot] = {
                'key': item_key,
                'count': count
            }

        return True, f"Transferred {count}x {item_key} from {sender} to {receiver}"

    def _execute_local_equip(
        self,
        state: Dict[str, Any],
        inventory_index: int
    ) -> Tuple[bool, str]:
        """
        Execute a local equip action.

        Modifies state in-place.

        Args:
            state: Agent state (will be modified)
            inventory_index: Index of item in inventory to equip

        Returns:
            Tuple of (success, message)
        """
        # Item to slot mapping (weapon slot = 4)
        ITEM_TO_SLOT = {
            'sword': 4, 'axe': 4, 'morningstar': 4, 'dagger': 4, 'pickaxe': 4,
            'staff': 4, 'magicstaff': 4, 'bow': 4, 'club': 4, 'mace': 4, 'hatchet': 4,
            'hammer': 4, 'spear': 4, 'scimitar': 4, 'battleaxe': 4,
            'ironsword': 4, 'ironaxe': 4, 'ironpickaxe': 4,
            'steelsword': 4, 'steelaxe': 4, 'steelpickaxe': 4,
            'goldsword': 4, 'goldaxe': 4, 'goldpickaxe': 4,
            'lightningstaff': 4, 'firestaff': 4, 'icestaff': 4,
            # Armour
            'leatherarmor': 0, 'leatherarmour': 0, 'chainmail': 0, 'platearmor': 0,
            'ironarmor': 0, 'steelarmor': 0, 'goldarmor': 0, 'wizardrobe': 0,
            # Boots
            'leatherboots': 1, 'ironboots': 1, 'steelboots': 1, 'goldboots': 1, 'wizardboots': 1,
            # Pendants
            'silverpendant': 2, 'goldpendant': 2, 'berylpendant': 2, 'rubypendant': 2,
            # Rings
            'goldring': 3, 'silverring': 3, 'bronzering': 3, 'topazring': 3,
            'emeraldring': 3, 'sapphirering': 3, 'diamondring': 3, 'rubyring': 3,
            # Arrows
            'arrow': 5, 'ironarrow': 5, 'steelarrow': 5, 'poisonarrow': 5,
        }

        inventory = state.get('inventory', [])
        equipment = state.get('equipment', {})

        # Validate inventory index
        if inventory_index < 0 or inventory_index >= len(inventory):
            return False, f"Invalid inventory index: {inventory_index}"

        item = inventory[inventory_index]
        if not item or not isinstance(item, dict):
            return False, f"No item at inventory index {inventory_index}"

        item_key = item.get('key', '').lower()
        slot = ITEM_TO_SLOT.get(item_key)

        if slot is None:
            return False, f"Item '{item_key}' is not equippable"

        # Swap: move current equipment to inventory, equip new item
        current_equipped = equipment.get(slot)

        # Equip the new item (take 1 from stack)
        item_count = item.get('count', 1)
        if item_count > 1:
            # Leave remaining in inventory
            inventory[inventory_index] = {'key': item.get('key'), 'count': item_count - 1}
        else:
            inventory[inventory_index] = None

        # Put old equipment in inventory if there was one
        if current_equipped and isinstance(current_equipped, dict):
            # Find empty slot for old equipment
            for i, inv_item in enumerate(inventory):
                if inv_item is None:
                    inventory[i] = current_equipped
                    break

        # Equip new item
        equipment[slot] = {'key': item.get('key'), 'count': 1}

        return True, f"Equipped {item.get('key')}"

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
        self.log(f"Max steps: {self.max_steps}, Beam size: {self.beam_size}, Actions/branch: {self.actions_per_branch}")
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
            # Debug: Show team inventory for first branch
            if branches:
                inv_summary = summarize_team_inventory(branches[0].agent_states)
                self.log(f"[DEBUG] {inv_summary}")

            # PHASE 1: Get observations for all branches in parallel
            self.log("Getting observations for all branches...")
            for branch in branches:
                branch.observations = self.get_observations(branch.agent_states)

            # PHASE 2: Propose actions for all branches in a single Claude call
            self.log("Proposing actions for all branches...")

            # Build branch data for combined proposal
            branch_data = [
                {
                    'agent_states': branch.agent_states,
                    'observations': branch.observations,
                    'history': branch.action_history
                }
                for branch in branches
            ]

            # Single Claude call for all branches
            branch_action_sets = propose_actions_multi_branch(
                self.task_context,
                branch_data,
                beam_count=self.actions_per_branch
            )

            # Inject arrow crafting action if fletcher has enough materials
            for branch_idx, branch in enumerate(branches):
                fletcher_name = None
                fletcher_sticks = 0
                fletcher_feathers = 0
                fletcher_arrows = 0
                for agent_name, state in branch.agent_states.items():
                    if 'fletcher' in agent_name.lower():
                        fletcher_name = agent_name
                        for item in state.get('inventory', []) or []:
                            if item and isinstance(item, dict):
                                key = item.get('key', '').lower()
                                count = item.get('count', 1) or 1
                                if key == 'stick':
                                    fletcher_sticks += count
                                elif key == 'feather':
                                    fletcher_feathers += count
                                elif key == 'arrow':
                                    fletcher_arrows += count

                # Inject arrow craft if:
                # 1. Fletcher has 10+ sticks AND 10+ feathers (first arrow), OR
                # 2. Fletcher has at least 1 stick AND 1 feather AND already has some arrows (continuing)
                should_inject = fletcher_name and (
                    (fletcher_sticks >= 10 and fletcher_feathers >= 10) or
                    (fletcher_sticks >= 1 and fletcher_feathers >= 1 and fletcher_arrows >= 1)
                )

                if should_inject:
                    # Force an arrow crafting action as first option
                    # count=1 means 1 batch = 10 arrows (consuming 10 sticks + 10 feathers)
                    arrow_action = {
                        fletcher_name: {'type': 'craft', 'skill': 'Fletching', 'itemKey': 'arrow', 'count': 1}
                    }
                    # Make others wait
                    for agent_name in branch.agent_states:
                        if agent_name != fletcher_name:
                            arrow_action[agent_name] = {'type': 'wait'}

                    # Insert at beginning of action sets
                    if branch_idx not in branch_action_sets:
                        branch_action_sets[branch_idx] = []
                    branch_action_sets[branch_idx].insert(0, arrow_action)
                    self.log(f"  [FORCED] Injected arrow crafting (sticks={fletcher_sticks}, feathers={fletcher_feathers}, arrows={fletcher_arrows})")

            for branch_idx in range(len(branches)):
                action_sets = branch_action_sets.get(branch_idx, [])
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

            branch_origins = []  # Track which source branch/action created each new branch
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
                        branch_origins.append((branch_idx + 1, action_idx + 1))

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
                kept_origins = [branch_origins[i] for i in selected_indices]
                self.log(f"Kept branches: {[f'B{o[0]}A{o[1]}' for o in kept_origins]}")
            else:
                branches = new_branches
                if branch_origins:
                    self.log(f"\nKept all {len(branches)} branches: {[f'B{o[0]}A{o[1]}' for o in branch_origins]}")

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
    actions_per_branch: int = 5,
    max_steps: int = 25,
    api_base: str = "http://localhost:7031",
    verbose: bool = True
) -> VerificationResult:
    """
    Run verification on a single task.

    Args:
        task_path: Path to task YAML
        beam_size: Beam size for search (branches to keep after pruning)
        actions_per_branch: Number of action sets to propose per branch
        max_steps: Maximum steps
        api_base: API base URL
        verbose: Print progress

    Returns:
        VerificationResult
    """
    verifier = BeamSearchVerifier(
        task_path=task_path,
        beam_size=beam_size,
        actions_per_branch=actions_per_branch,
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
