"""
Game tools for interacting with Kaetram game server APIs
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from config import (
    KAETRAM_BASE_URL, 
    KAETRAM_API_ENDPOINTS, 
    REQUEST_TIMEOUT,
    OBSERVATION_RADIUS,
    MAX_RETRIES
)


class KaetramGameTools:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.session.timeout = REQUEST_TIMEOUT
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Kaetram API with retry logic"""
        url = f"{KAETRAM_BASE_URL}{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params)
                elif method == "POST":
                    response = self.session.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    return {"status": "error", "message": f"Request failed after {MAX_RETRIES} attempts: {str(e)}"}
                time.sleep(1)
        
        return {"status": "error", "message": "Max retries exceeded"}

    def create_character(self, arguments: Dict[str, Any]) -> str:
        """Create a new AI character in the game"""
        username = arguments.get("username", "QwenAgent")
        password = arguments.get("password", "qwen123456")
        
        data = {
            "username": username,
            "password": password
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["create"], data)
        
        if result.get("status") == "success":
            self.token = result.get("token")
            return f"Character {username} created successfully. Token obtained."
        else:
            return f"Failed to create character: {result.get('message', 'Unknown error')}"

    def login_character(self, arguments: Dict[str, Any]) -> str:
        """Login with existing character"""
        username = arguments.get("username", "QwenAgent")
        password = arguments.get("password", "qwen123456")
        
        data = {
            "username": username,
            "password": password
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["login"], data)
        
        if result.get("status") == "success":
            self.token = result.get("token")
            return f"Character {username} logged in successfully. Token obtained."
        else:
            return f"Failed to login: {result.get('message', 'Unknown error')}"

    def move_character(self, arguments: Dict[str, Any]) -> str:
        """Move character to specified coordinates"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        x = arguments.get("x")
        y = arguments.get("y")
        
        if x is None or y is None:
            return "Error: Both x and y coordinates are required for movement."
        
        data = {
            "token": self.token,
            "x": int(x),
            "y": int(y)
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["move"], data)
        
        if result.get("status") == "success":
            start_pos = result.get("startPosition", {})
            target_pos = result.get("targetPosition", {})
            return f"Character moved from ({start_pos.get('x')}, {start_pos.get('y')}) to ({target_pos.get('x')}, {target_pos.get('y')})"
        else:
            return f"Failed to move character: {result.get('message', 'Unknown error')}"

    def teleport_character(self, arguments: Dict[str, Any]) -> str:
        """Teleport character instantly to specified coordinates"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        x = arguments.get("x")
        y = arguments.get("y")
        with_animation = arguments.get("withAnimation", False)
        
        if x is None or y is None:
            return "Error: Both x and y coordinates are required for teleportation."
        
        data = {
            "token": self.token,
            "x": int(x),
            "y": int(y),
            "withAnimation": bool(with_animation)
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["teleport"], data)
        
        if result.get("status") == "success":
            prev_pos = result.get("previousPosition", {})
            new_pos = result.get("newPosition", {})
            animation_status = "with animation" if result.get("withAnimation", False) else "without animation"
            return f"Character teleported from ({prev_pos.get('x')}, {prev_pos.get('y')}) to ({new_pos.get('x')}, {new_pos.get('y')}) {animation_status}"
        else:
            return f"Failed to teleport character: {result.get('message', 'Unknown error')}"

    def send_chat_message(self, arguments: Dict[str, Any]) -> str:
        """Send chat message in the game"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        message = arguments.get("message", "")
        is_global = arguments.get("global", False)
        
        if not message:
            return "Error: Message content is required."
        
        data = {
            "token": self.token,
            "message": message,
            "global": is_global
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["chat"], data)
        
        if result.get("status") == "success":
            chat_type = "global" if is_global else "local"
            return f"Chat message sent successfully ({chat_type}): {message}"
        else:
            return f"Failed to send chat message: {result.get('message', 'Unknown error')}"

    def observe_environment(self, arguments: Dict[str, Any]) -> str:
        """Observe the surrounding environment"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        radius = arguments.get("radius", OBSERVATION_RADIUS)
        
        params = {
            "token": self.token,
            "radius": radius
        }
        
        result = self._make_request("GET", KAETRAM_API_ENDPOINTS["observe"], params=params)
        
        if result.get("status") == "success":
            # The entire result is the observation data, no nested "observations" field
            return f"Environment observation (radius {radius}): {json.dumps(result, indent=2)}"
        else:
            return f"Failed to observe environment: {result.get('message', 'Unknown error')}"

    def enter_portal(self, arguments: Dict[str, Any]) -> str:
        """Enter a portal or warp point"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        data = {
            "token": self.token
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["enter"], data)
        
        if result.get("status") == "success":
            destination = result.get("destination", "unknown")
            prev_pos = result.get("previousPosition", {})
            return f"Entered portal successfully. Moved from ({prev_pos.get('x')}, {prev_pos.get('y')}) to {destination}"
        else:
            return f"Failed to enter portal: {result.get('message', 'Unknown error')}"

    def stop_action(self, arguments: Dict[str, Any]) -> str:
        """Stop current movement or combat"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        data = {
            "token": self.token
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["stop"], data)
        
        if result.get("status") == "success":
            stopped = result.get("stopped", {})
            return f"Actions stopped: movement={stopped.get('movement', False)}, combat={stopped.get('combat', False)}"
        else:
            return f"Failed to stop actions: {result.get('message', 'Unknown error')}"

    def equip_item(self, arguments: Dict[str, Any]) -> str:
        """Equip an item from inventory"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        index = arguments.get("index")
        
        if index is None:
            return "Error: Item inventory index is required."
        
        data = {
            "token": self.token,
            "index": int(index)
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["equip"], data)
        
        if result.get("status") == "success":
            item = result.get("item", {})
            return f"Item equipped successfully: {item.get('name', 'Unknown')} (type: {item.get('equipmentType', 'Unknown')})"
        else:
            return f"Failed to equip item: {result.get('message', 'Unknown error')}"

    def collect_resource(self, arguments: Dict[str, Any]) -> str:
        """Collect a resource using appropriate skill"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required for resource collection."
        
        data = {
            "token": self.token,
            "targetInstance": target_instance
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["collect"], data)
        
        if result.get("status") == "success":
            resource = result.get("resource", {})
            return f"Started collecting resource: {resource.get('name', 'Unknown')} at ({resource.get('x')}, {resource.get('y')})"
        else:
            return f"Failed to collect resource: {result.get('message', 'Unknown error')}"

    def target_entity(self, arguments: Dict[str, Any]) -> str:
        """Target an entity for interaction or combat (Note: This uses attack API to target)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required."
        
        # Use attack API with targetInstance for targeting
        data = {
            "token": self.token,
            "targetInstance": target_instance
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["attack"], data)
        
        if result.get("status") == "success":
            return f"Targeted entity successfully: {result.get('message', 'Attack initiated')}"
        else:
            return f"Failed to target entity: {result.get('message', 'Unknown error')}"

    def attack_target(self, arguments: Dict[str, Any]) -> str:
        """Attack the currently targeted entity"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required for attack."
        
        data = {
            "token": self.token,
            "targetInstance": target_instance
        }
        
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["attack"], data)
        
        if result.get("status") == "success":
            # Attack API only returns status and message
            return f"Attack initiated: {result.get('message', 'Attack started successfully')}"
        else:
            return f"Failed to attack: {result.get('message', 'Unknown error')}" 