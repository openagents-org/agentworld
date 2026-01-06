"""
Verifier Adapter Module

Converts simulation states to trajectory format for Python verifiers.
"""

import sys
import os
from typing import Dict, List, Any, Tuple

# Add parent directory to path for importing task_verifier1
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def state_to_inventory_items(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert simulation state inventory to verifier format."""
    items = []
    for item in state.get('inventory', []):
        if item and item.get('key'):
            items.append({
                'key': item['key'],
                'count': item.get('count', 1)
            })
    return items


def state_to_equipment_items(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert simulation state equipment to verifier format."""
    items = []
    slot_names = {0: 'armour', 1: 'boots', 2: 'pendant', 3: 'ring', 4: 'weapon', 5: 'arrows'}
    for slot, item in state.get('equipment', {}).items():
        if item and item.get('key'):
            items.append({
                'slot': slot_names.get(int(slot), str(slot)),
                'key': item['key'],
                'count': item.get('count', 1)
            })
    return items


def state_to_status_string(state: Dict[str, Any]) -> str:
    """Convert simulation state to status string format."""
    hp = state.get('hitPoints', 100)
    max_hp = state.get('maxHitPoints', 100)
    mana = state.get('mana', 0)
    max_mana = state.get('maxMana', 0)
    x = state.get('x', 0)
    y = state.get('y', 0)

    return f"❤️{hp}/{max_hp} | 💎{mana}/{max_mana} | 📍({x},{y})"


def action_to_string(action: Dict[str, Any]) -> str:
    """Convert action dict to action string."""
    action_type = action.get('type', 'unknown')

    if action_type == 'move':
        pickup_items = action.get('pickupItems', [])
        if pickup_items:
            items_str = ', '.join(f"{i['count']}x {i['key']}" for i in pickup_items)
            return f"move(x={action.get('x')}, y={action.get('y')}, pickup=[{items_str}])"
        return f"move(x={action.get('x')}, y={action.get('y')})"
    elif action_type == 'craft':
        return f"craft_item(skill={action.get('skill')}, itemKey={action.get('itemKey')}, count={action.get('count', 1)})"
    elif action_type == 'collect':
        return f"harvest_resource({action.get('resourceType')}, resourceKey={action.get('resourceKey')})"
    elif action_type == 'attack':
        return f"attack(targetInstance={action.get('targetInstance')})"
    elif action_type == 'equip':
        return f"equip(inventoryIndex={action.get('inventoryIndex')})"
    elif action_type == 'unequip':
        return f"unequip(equipmentSlot={action.get('equipmentSlot')})"
    elif action_type == 'eat':
        return f"eat(inventoryIndex={action.get('inventoryIndex')})"
    elif action_type == 'drop':
        return f"drop_item(inventoryIndex={action.get('inventoryIndex')}, count={action.get('count', 1)})"
    elif action_type == 'use':
        return f"use_item(inventoryIndex={action.get('inventoryIndex')})"
    elif action_type == 'enter':
        return "enter_warp()"
    elif action_type == 'wait':
        return "wait()"
    elif action_type == 'pickup':
        return f"pickup(itemKey={action.get('itemKey')}, count={action.get('count', 1)})"
    else:
        return f"{action_type}({action})"


def states_to_trajectory(
    task_id: str,
    agent_states: Dict[str, Dict[str, Any]],
    action_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Convert simulation states and action history to trajectory JSON format.

    The trajectory format expected by task_verifier1.py:
    {
        "task_id": "task_01_magic_staff",
        "rounds": [
            {
                "round": 1,
                "actions": [
                    {
                        "agent_name": "agent1",
                        "action": "move(x=100, y=50)",
                        "observation": {
                            "status": "success",
                            "inventory": {"items": [...]},
                            "equipment": {"items": [...]}
                        },
                        "status": "❤️100/100 | 💎50/50 | 📍(100,50)"
                    }
                ]
            }
        ]
    }

    Args:
        task_id: Task identifier (e.g., "task_01_magic_staff")
        agent_states: Current state for each agent {name: state}
        action_history: List of action results from beam search

    Returns:
        Trajectory dictionary in verifier format
    """
    rounds = []

    # Build rounds from action history
    for round_num, step_actions in enumerate(action_history, start=1):
        round_actions = []

        for agent_name, action_result in step_actions.items():
            action = action_result.get('action', {})
            success = action_result.get('success', False)
            message = action_result.get('message', '')
            state_after = action_result.get('state_after', agent_states.get(agent_name, {}))

            # Build observation
            observation = {
                'status': 'success' if success else 'failed',
                'message': message,
                'inventory': {
                    'items': state_to_inventory_items(state_after)
                },
                'equipment': {
                    'items': state_to_equipment_items(state_after)
                },
                'position': {
                    'x': state_after.get('x', 0),
                    'y': state_after.get('y', 0)
                }
            }

            round_actions.append({
                'agent_name': agent_name,
                'action': action_to_string(action),
                'observation': observation,
                'status': state_to_status_string(state_after)
            })

        rounds.append({
            'round': round_num,
            'actions': round_actions
        })

    # Add a final round with current states if action_history is empty
    # or to ensure final state is captured
    if agent_states:
        final_actions = []
        for agent_name, state in agent_states.items():
            observation = {
                'status': 'current',
                'inventory': {
                    'items': state_to_inventory_items(state)
                },
                'equipment': {
                    'items': state_to_equipment_items(state)
                },
                'position': {
                    'x': state.get('x', 0),
                    'y': state.get('y', 0)
                }
            }
            final_actions.append({
                'agent_name': agent_name,
                'action': 'final_state()',
                'observation': observation,
                'status': state_to_status_string(state)
            })

        if not rounds or rounds[-1]['actions'] != final_actions:
            rounds.append({
                'round': len(rounds) + 1,
                'actions': final_actions
            })

    return {
        'task_id': task_id,
        'rounds': rounds
    }


def extract_base_task_id(task_id: str) -> str:
    """
    Extract base task ID from full task ID.

    Examples:
        task_01_magic_staff_v1 -> task_01
        task_02_arrow_production_v2 -> task_02
        task_03 -> task_03
    """
    import re
    # Match task_XX pattern at the start
    match = re.match(r'(task_\d+)', task_id)
    if match:
        return match.group(1)
    return task_id


def verify_task(task_id: str, trajectory: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Run Python verifier on trajectory.

    Args:
        task_id: Task identifier
        trajectory: Trajectory dict from states_to_trajectory

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        import task_verifier1
        # Extract base task ID (e.g., task_01_magic_staff_v1 -> task_01)
        base_task_id = extract_base_task_id(task_id)
        result, message = task_verifier1.verify_task(trajectory, base_task_id)
        return (result == 1, message)
    except ImportError:
        return (False, "Could not import task_verifier1")
    except Exception as e:
        return (False, f"Verifier error: {str(e)}")


def quick_verify_state(
    task_id: str,
    agent_states: Dict[str, Dict[str, Any]],
    action_history: List[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Quick verification of current states.

    Args:
        task_id: Task identifier
        agent_states: Current state for each agent
        action_history: Optional action history

    Returns:
        Tuple of (success: bool, message: str)
    """
    trajectory = states_to_trajectory(
        task_id,
        agent_states,
        action_history or []
    )
    return verify_task(task_id, trajectory)


def check_basic_objectives(
    task_id: str,
    agent_states: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Quick check of common objectives without full verifier.

    This provides faster feedback for common patterns.

    Args:
        task_id: Task identifier
        agent_states: Current state for each agent

    Returns:
        Dictionary with check results
    """
    results = {
        'all_alive': True,
        'total_items': 0,
        'items_by_agent': {},
        'equipment_by_agent': {},
        'positions': {}
    }

    for agent_name, state in agent_states.items():
        # Check alive
        if state.get('dead', False) or state.get('hitPoints', 0) <= 0:
            results['all_alive'] = False

        # Count inventory items
        agent_items = {}
        for item in state.get('inventory', []):
            if item and item.get('key'):
                key = item['key'].lower()
                count = item.get('count', 1)
                agent_items[key] = agent_items.get(key, 0) + count
                results['total_items'] += count
        results['items_by_agent'][agent_name] = agent_items

        # Check equipment
        agent_equipment = {}
        for slot, item in state.get('equipment', {}).items():
            if item and item.get('key'):
                agent_equipment[int(slot)] = item['key'].lower()
        results['equipment_by_agent'][agent_name] = agent_equipment

        # Record position
        results['positions'][agent_name] = (state.get('x', 0), state.get('y', 0))

    return results


if __name__ == '__main__':
    # Test the module
    print("Testing verifier adapter...")

    # Create test states
    test_states = {
        'wizard_agent': {
            'x': 392, 'y': 3,
            'hitPoints': 100, 'maxHitPoints': 100,
            'mana': 250, 'maxMana': 250,
            'level': 10, 'dead': False,
            'skills': {11: 1000},  # Crafting
            'inventory': [
                {'key': 'staff', 'count': 1},
                {'key': 'bead', 'count': 1}
            ],
            'equipment': {4: {'key': 'staff', 'count': 1}},
            'poisoned': False, 'stunned': False
        }
    }

    # Test trajectory conversion
    trajectory = states_to_trajectory('task_01_magic_staff', test_states, [])
    print(f"Generated trajectory with {len(trajectory['rounds'])} rounds")

    # Test basic objective check
    objectives = check_basic_objectives('task_01_magic_staff', test_states)
    print(f"Basic objectives: {objectives}")
