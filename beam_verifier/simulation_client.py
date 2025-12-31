"""
Simulation Client Module

HTTP wrapper for the simulation API endpoints.
"""

import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class SimulationResult:
    """Result of a simulation action."""
    success: bool
    message: str
    state_after: Dict[str, Any]
    details: Optional[Dict[str, Any]] = None


class SimulationClient:
    """
    HTTP client for the AgentWorld simulation API.

    The simulation API provides stateless simulation of agent actions
    without requiring actual game sessions.
    """

    def __init__(self, api_base: str = "http://localhost:7031"):
        """
        Initialize the simulation client.

        Args:
            api_base: Base URL for the API server
        """
        self.api_base = api_base.rstrip('/')
        self.session = requests.Session()
        # Set timeout for requests
        self.timeout = 30

    def observe(self, x: int, y: int, radius: int = 15) -> Dict[str, Any]:
        """
        Get environment observation at a position.

        Args:
            x: X coordinate
            y: Y coordinate
            radius: Observation radius (default 15)

        Returns:
            Dictionary with environment information including:
            - location: current position info
            - map: map metadata
            - mobs: nearby monsters
            - resources: nearby resources (trees, rocks, etc.)
            - players: nearby players
            - collisions: blocked tiles
            - doors: teleporters
            - entries: warps/portals
        """
        url = f"{self.api_base}/ai/simulation/observe"
        params = {'x': x, 'y': y, 'radius': radius}

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'error': str(e),
                'location': {'x': x, 'y': y, 'regionId': -1, 'mapName': 'unknown'},
                'mobs': [],
                'resources': [],
                'players': [],
                'collisions': [],
                'doors': [],
                'entries': []
            }

    def act(self, state: Dict[str, Any], action: Dict[str, Any]) -> SimulationResult:
        """
        Execute an action on a given state.

        Args:
            state: Current SimulationState dictionary
            action: Action to execute (type-specific parameters)

        Returns:
            SimulationResult with success status, message, and new state
        """
        url = f"{self.api_base}/ai/simulation/act"
        payload = {'state': state, 'action': action}

        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return SimulationResult(
                success=data.get('success', False),
                message=data.get('message', ''),
                state_after=data.get('state_after', state),
                details=data.get('details')
            )
        except requests.RequestException as e:
            return SimulationResult(
                success=False,
                message=f"API error: {str(e)}",
                state_after=state
            )

    def move(self, state: Dict[str, Any], x: int, y: int) -> SimulationResult:
        """Move to a position."""
        return self.act(state, {'type': 'move', 'x': x, 'y': y})

    def craft(self, state: Dict[str, Any], skill: str, item_key: str, count: int = 1) -> SimulationResult:
        """Craft an item."""
        return self.act(state, {'type': 'craft', 'skill': skill, 'itemKey': item_key, 'count': count})

    def collect(self, state: Dict[str, Any], resource_type: str, resource_key: str) -> SimulationResult:
        """Collect from a resource (tree, rock, fish, foraging)."""
        return self.act(state, {'type': 'collect', 'resourceType': resource_type, 'resourceKey': resource_key})

    def attack(self, state: Dict[str, Any], target_instance: str) -> SimulationResult:
        """Attack a target (informational only)."""
        return self.act(state, {'type': 'attack', 'targetInstance': target_instance})

    def equip(self, state: Dict[str, Any], inventory_index: int) -> SimulationResult:
        """Equip an item from inventory."""
        return self.act(state, {'type': 'equip', 'inventoryIndex': inventory_index})

    def unequip(self, state: Dict[str, Any], equipment_slot: int) -> SimulationResult:
        """Unequip an item to inventory."""
        return self.act(state, {'type': 'unequip', 'equipmentSlot': equipment_slot})

    def eat(self, state: Dict[str, Any], inventory_index: int) -> SimulationResult:
        """Eat an item for healing."""
        return self.act(state, {'type': 'eat', 'inventoryIndex': inventory_index})

    def drop(self, state: Dict[str, Any], inventory_index: int, count: Optional[int] = None) -> SimulationResult:
        """Drop an item from inventory."""
        action = {'type': 'drop', 'inventoryIndex': inventory_index}
        if count is not None:
            action['count'] = count
        return self.act(state, action)

    def use(self, state: Dict[str, Any], inventory_index: int) -> SimulationResult:
        """Use an item (potion, etc.)."""
        return self.act(state, {'type': 'use', 'inventoryIndex': inventory_index})

    def enter(self, state: Dict[str, Any]) -> SimulationResult:
        """Enter a warp/portal at current position."""
        return self.act(state, {'type': 'enter'})

    def health_check(self) -> bool:
        """Check if the API server is reachable."""
        try:
            # Try to observe at origin
            response = self.session.get(
                f"{self.api_base}/ai/simulation/observe",
                params={'x': 0, 'y': 0, 'radius': 1},
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def is_position_blocked(self, x: int, y: int) -> bool:
        """
        Check if a position is blocked by collision.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if position is blocked, False if walkable
        """
        obs = self.observe(x, y, radius=1)
        collisions = obs.get('collisions', [])

        # Check if our exact position is in collisions
        for collision in collisions:
            if collision.get('x') == x and collision.get('y') == y:
                return True
        return False

    def find_walkable_position(self, x: int, y: int, max_radius: int = 50) -> tuple:
        """
        Find a walkable position near the given coordinates.

        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            max_radius: Maximum search radius

        Returns:
            Tuple of (x, y) for a walkable position, or original if none found
        """
        # First check if original position is walkable
        if not self.is_position_blocked(x, y):
            return (x, y)

        # Search in expanding spiral pattern
        for radius in range(1, max_radius + 1):
            # Check positions at this radius
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Only check positions on the edge of the square
                    if abs(dx) != radius and abs(dy) != radius:
                        continue

                    test_x, test_y = x + dx, y + dy
                    if test_x >= 0 and test_y >= 0:
                        if not self.is_position_blocked(test_x, test_y):
                            return (test_x, test_y)

        # Fallback: try known walkable areas
        known_walkable = [(50, 50), (100, 100), (239, 30), (150, 150)]
        for wx, wy in known_walkable:
            if not self.is_position_blocked(wx, wy):
                return (wx, wy)

        return (x, y)  # Return original if nothing found


def simulate_action_sequence(
    client: SimulationClient,
    initial_state: Dict[str, Any],
    actions: list
) -> tuple:
    """
    Simulate a sequence of actions starting from an initial state.

    Args:
        client: SimulationClient instance
        initial_state: Starting state
        actions: List of action dictionaries

    Returns:
        Tuple of (final_state, success_count, messages)
    """
    state = initial_state.copy()
    success_count = 0
    messages = []

    for action in actions:
        result = client.act(state, action)
        messages.append(f"{action['type']}: {result.message}")

        if result.success:
            success_count += 1
            state = result.state_after
        else:
            # Continue with original state on failure
            pass

    return state, success_count, messages


if __name__ == '__main__':
    # Test the client
    client = SimulationClient()

    print("Testing simulation client...")

    # Test health check
    if client.health_check():
        print("API server is reachable")

        # Test observe
        obs = client.observe(388, 3, 15)
        print(f"\nObservation at (388, 3):")
        print(f"  Map: {obs.get('map', {}).get('name', 'unknown')}")
        print(f"  Resources: {len(obs.get('resources', []))} nearby")
        print(f"  Mobs: {len(obs.get('mobs', []))} nearby")

        # Test act with a simple state
        test_state = {
            'x': 388,
            'y': 3,
            'hitPoints': 100,
            'maxHitPoints': 100,
            'mana': 50,
            'maxMana': 50,
            'level': 10,
            'dead': False,
            'skills': {0: 1000, 3: 1000},  # lumberjacking, health
            'inventory': [None] * 25,
            'equipment': {0: None, 1: None, 2: None, 3: None, 4: None, 5: None},
            'poisoned': False,
            'stunned': False
        }

        result = client.move(test_state, 387, 3)
        print(f"\nMove test: success={result.success}, message={result.message}")
    else:
        print("API server is not reachable")
