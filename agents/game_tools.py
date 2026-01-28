"""
Game tools for interacting with Kaetram game server APIs
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from config import (
    AGENTWORLD_BASE_URL, 
    AGENTWORLD_API_ENDPOINTS, 
    REQUEST_TIMEOUT,
    OBSERVATION_RADIUS,
    MAX_RETRIES
)


class KaetramGameTools:
    # Class variable to store logger for detailed error reporting
    _global_logger = None
    
    def __init__(self, base_url: Optional[str] = None, logger=None, debug_prints: bool = False):
        self.base_url = base_url or AGENTWORLD_BASE_URL
        self.token = None
        self.session = requests.Session()
        self.session.timeout = REQUEST_TIMEOUT
        self.logger = logger  # Store logger for detailed error reporting
        self._last_observation_data = None  # Initialize observation data storage
        self.debug_prints = debug_prints  # Control debug print statements
        
    @classmethod
    def set_global_logger(cls, logger):
        """Set a global logger for all instances"""
        cls._global_logger = logger
        
    def _log_message(self, message: str, level: str = "info"):
        """Log message using available logger"""
        logger = self.logger or self._global_logger
        if logger:
            if level == "error":
                logger.error(message)
            elif level == "debug":
                logger.debug(message)
            elif level == "warning":
                logger.warning(message)
            else:
                logger.info(message)
    
    def _debug_print(self, message: str):
        """Print debug message only if debug_prints is enabled"""
        if self.debug_prints:
            print(message)
    
    def get_last_observation_data(self) -> Optional[Dict[str, Any]]:
        """Get the last observation data for logging purposes"""
        return getattr(self, '_last_observation_data', None)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Kaetram API with retry logic and detailed error logging"""
        url = f"{self.base_url}{endpoint}"
        
        # Enhanced logging for all API calls
        self._log_message(f"🌐 [API REQUEST] {method} {endpoint}", "debug")
        if data:
            self._log_message(f"   📤 Request Data: {json.dumps(data, ensure_ascii=False)}", "debug")
        if params:
            self._log_message(f"   📤 Request Params: {json.dumps(params, ensure_ascii=False)}", "debug")
        
        for attempt in range(MAX_RETRIES):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params)
                elif method == "POST":
                    response = self.session.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Log response details for all calls
                self._log_message(f"🌐 [API RESPONSE] Status: {response.status_code} for {endpoint}", "debug")
                
                # If response is not successful, log detailed error information
                if not response.ok:
                    error_details = {
                        "status_code": response.status_code,
                        "response_text": response.text,
                        "response_headers": dict(response.headers),
                        "url": url,
                        "method": method,
                        "endpoint": endpoint,
                        "attempt": attempt + 1,
                        "request_data": data,
                        "request_params": params
                    }
                    
                    # Try to parse JSON response for better error details
                    try:
                        response_json = response.json()
                        error_details["response_json"] = response_json
                        error_message = response_json.get("message", "No error message provided")
                    except:
                        error_message = response.text[:200] if response.text else "No response text"
                    
                    # Log detailed error information
                    error_lines = [
                        f"❌ [HTTP ERROR] {method} {endpoint} - Attempt {attempt + 1}/{MAX_RETRIES}",
                        f"   📍 URL: {url}",
                        f"   📊 Status Code: {response.status_code}",
                        f"   💬 Error Message: {error_message}",
                        f"   📤 Request Data: {json.dumps(data, ensure_ascii=False) if data else 'None'}",
                        f"   📤 Request Params: {json.dumps(params, ensure_ascii=False) if params else 'None'}",
                        f"   📥 Response Headers: {json.dumps(dict(response.headers), ensure_ascii=False)}",
                        f"   📥 Full Response: {response.text[:1000]}"
                    ]
                    
                    for line in error_lines:
                        self._log_message(line, "error")
                    
                    # For 400 errors (game logic errors), return immediately without retrying
                    # These are not server errors - they are valid responses indicating the action failed
                    # The agent should receive this feedback to adjust its behavior
                    if response.status_code == 400:
                        self._log_message(f"⚠️ [GAME LOGIC ERROR] {endpoint}: {error_message}", "warning")
                        return {
                            "status": "error",
                            "message": error_message,
                            "error_type": "game_logic",
                            "details": error_details
                        }

                # Only raise for server errors (5xx) which should be retried
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                error_details = {
                    "status_code": getattr(e.response, 'status_code', 'Unknown'),
                    "response_text": getattr(e.response, 'text', 'No response text'),
                    "url": url,
                    "method": method,
                    "endpoint": endpoint,
                    "attempt": attempt + 1,
                    "request_data": data,
                    "request_params": params
                }

                # Try to parse JSON response for better error details
                try:
                    response_json = e.response.json()
                    error_details["response_json"] = response_json
                    error_message = response_json.get("message", "No error message provided")
                except:
                    error_message = e.response.text[:200] if e.response.text else "No response text"

                # For 4xx client errors (game logic errors), return immediately without retrying
                # These indicate the action is invalid, not a server problem
                status_code = error_details['status_code']
                if isinstance(status_code, int) and 400 <= status_code < 500:
                    self._log_message(f"⚠️ [GAME LOGIC ERROR] {endpoint}: {error_message}", "warning")
                    return {
                        "status": "error",
                        "message": error_message,
                        "error_type": "game_logic",
                        "details": error_details
                    }

                # Log detailed error information for server errors (5xx)
                error_lines = [
                    f"❌ [SERVER ERROR] {method} {endpoint} - Attempt {attempt + 1}/{MAX_RETRIES}",
                    f"   📍 URL: {url}",
                    f"   📊 Status Code: {status_code}",
                    f"   💬 Error Message: {error_message}",
                    f"   📤 Request Data: {json.dumps(data, ensure_ascii=False) if data else 'None'}",
                    f"   📤 Request Params: {json.dumps(params, ensure_ascii=False) if params else 'None'}"
                ]

                for line in error_lines:
                    self._log_message(line, "error")

                if attempt == MAX_RETRIES - 1:
                    final_error = f"Server error {status_code} after {MAX_RETRIES} attempts: {str(e)}"
                    self._log_message(f"❌ FINAL SERVER ERROR: {final_error}", "error")
                    return {
                        "status": "error",
                        "message": final_error,
                        "error_type": "server_error",
                        "details": error_details
                    }
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                error_lines = [
                    f"❌ [REQUEST ERROR] {method} {endpoint} - Attempt {attempt + 1}/{MAX_RETRIES}",
                    f"   📍 URL: {url}",
                    f"   💬 Error: {str(e)}",
                    f"   📤 Request Data: {json.dumps(data, ensure_ascii=False) if data else 'None'}",
                    f"   📤 Request Params: {json.dumps(params, ensure_ascii=False) if params else 'None'}"
                ]
                
                for line in error_lines:
                    self._log_message(line, "error")
                
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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["create"], data)
        
        if result.get("status") == "success":
            self.token = result.get("token")
            return f"Character {username} created successfully. Token obtained."
        else:
            return f"Failed to create character: {result.get('message', 'Unknown error')}"

    def login_character(self, arguments: Dict[str, Any]) -> str:
        """Login with existing character. Supports force login to disconnect existing sessions."""
        username = arguments.get("username", "QwenAgent")
        password = arguments.get("password", "qwen123456")
        force = arguments.get("force", False)

        data = {
            "username": username,
            "password": password,
            "force": force
        }

        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["login"], data)

        if result.get("status") == "success":
            self.token = result.get("token")
            return f"Character {username} logged in successfully. Token obtained."
        else:
            error_msg = result.get('message', 'Unknown error')

            # If player is already logged in and we haven't tried force login yet, retry with force
            if "already logged in" in error_msg.lower() and not force:
                self._debug_print(f"Player {username} already logged in, attempting force login...")
                # Retry with force=True
                data["force"] = True
                result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["login"], data)

                if result.get("status") == "success":
                    self.token = result.get("token")
                    return f"Character {username} force logged in successfully (previous session disconnected). Token obtained."
                else:
                    return f"Failed to force login: {result.get('message', 'Unknown error')}"

            return f"Failed to login: {error_msg}"

    def logout_character(self) -> str:
        """Logout the current character and invalidate token"""
        if not self.token:
            return "No active session to logout"
        
        data = {"token": self.token}
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["logout"], data)
        
        if result.get("status") == "success":
            old_token = self.token[:10] if self.token else "unknown"
            self.token = None  # Clear token after successful logout
            return f"Successfully logged out (token: {old_token}...)"
        else:
            return f"Failed to logout: {result.get('message', 'Unknown error')}"

    def move_character(self, arguments: Dict[str, Any]) -> str:
        """Move character to specified coordinates"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        x = arguments.get("x")
        y = arguments.get("y")
        
        if x is None or y is None:
            return "Error: Both x and y coordinates are required for movement."
        
        target_x = int(x)
        target_y = int(y)
        
        # Get current player position to check distance
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 5})
        
        if observe_result.get("status") != "success":
            return "Error: Could not determine current position to validate movement distance."
        
        location = observe_result.get("location", {})
        current_x = location.get("x")
        current_y = location.get("y")
        
        if current_x is None or current_y is None:
            return "Error: Could not determine current player position."
        
        # Calculate distance using Manhattan distance (same as server)
        distance = abs(target_x - current_x) + abs(target_y - current_y)
        # Distance limit removed - allow long-distance movement for multi-agent coordination
        
        data = {
            "token": self.token,
            "x": target_x,
            "y": target_y
        }
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], data)

        if result.get("status") == "success":
            start_pos = result.get("startPosition", {})
            target_pos = result.get("targetPosition", {})
            return f"Character moved from ({start_pos.get('x')}, {start_pos.get('y')}) to ({target_pos.get('x')}, {target_pos.get('y')}) (distance: {distance} tiles)"
        else:
            error_msg = result.get('message', 'Unknown error')
            details = result.get('details', {})
            response_json = details.get('response_json', {})

            # Check if this is a distance limit error and provide helpful guidance
            if response_json and ('distance' in response_json or 'maxDistance' in response_json):
                # Extract distance information from error response
                current_pos = response_json.get('currentPosition', {})
                target_pos = response_json.get('targetPosition', {})
                actual_distance = response_json.get('distance', distance)
                max_distance = response_json.get('maxDistance', 120)
                api_error_msg = response_json.get('message', error_msg)

                return (f"Failed to move character: {api_error_msg} "
                       f"Current position: ({current_pos.get('x', current_x)}, {current_pos.get('y', current_y)}), "
                       f"Target: ({target_pos.get('x', target_x)}, {target_pos.get('y', target_y)}), "
                       f"Distance: {actual_distance} tiles, Maximum allowed: {max_distance} tiles. "
                       f"SOLUTION: Break this into multiple moves. Move to an intermediate point first, then continue to your target.")

            return f"Failed to move character: {error_msg}"

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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["teleport"], data)
        
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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["chat"], data)
        
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
        
        result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params=params)
        
        if result.get("status") == "success":
            # Enhance the observation data by categorizing resources
            enhanced_result = dict(result)
            
            # Get the generic resources array from the API response
            resources = result.get("resources", [])
            
            # Categorize resources by type (based on entity type checking from the game code)
            trees = []
            rocks = []
            fish_spots = []
            foraging = []
            
            for resource in resources:
                resource_name = resource.get("name", "").lower()
                
                # Categorize based on common patterns in resource names
                # Trees: oak, palm, pine, willow, bloodwood, etc.
                if any(tree_type in resource_name for tree_type in [
                    "oak", "palm", "pine", "willow", "bloodwood", "tree", "wood"
                ]):
                    trees.append(resource)
                
                # Rocks/Mining: ore, rock, coal, gem names, etc.
                elif any(rock_type in resource_name for rock_type in [
                    "rock", "ore", "coal", "copper", "tin", "iron", "gold", "nisoc", 
                    "cinnabar", "pythar", "ibo", "moonrock", "topaz", "beryl", 
                    "lapislazuli", "citrine", "taaffeite", "ruby", "peridot", 
                    "opal", "emerald", "amethyst"
                ]):
                    rocks.append(resource)
                
                # Fishing: fish, shrimp, tuna, jellyfish, clam, etc.
                elif any(fish_type in resource_name for fish_type in [
                    "fish", "shrimp", "tuna", "jellyfish", "clam", "fishing", "spot"
                ]):
                    fish_spots.append(resource)
                
                # Foraging: plant, berry, corn, lily, tomato, peach, etc.
                elif any(plant_type in resource_name for plant_type in [
                    "plant", "berry", "corn", "lily", "tomato", "peach", "herb", 
                    "flower", "fruit", "vegetable"
                ]):
                    foraging.append(resource)
                
                # Fallback: if we can't categorize, check entity type number
                # Based on the game code, different entity types have different numbers
                else:
                    entity_type = resource.get("type", 0)
                    # These are educated guesses based on typical entity type patterns
                    if entity_type == 10:  # Trees often use type 10
                        trees.append(resource)
                    elif entity_type == 11:  # Rocks might use type 11
                        rocks.append(resource)
                    elif entity_type == 12:  # Fishing spots might use type 12
                        fish_spots.append(resource)
                    elif entity_type == 13:  # Foraging might use type 13
                        foraging.append(resource)
                    else:
                        # If we still can't categorize, add to trees as default
                        trees.append(resource)
            
            # Add the categorized resources to the enhanced result
            enhanced_result["trees"] = trees
            enhanced_result["rocks"] = rocks  
            enhanced_result["fishSpots"] = fish_spots
            enhanced_result["foraging"] = foraging
            
            # Remove the generic resources array since we've categorized them
            if "resources" in enhanced_result:
                del enhanced_result["resources"]

            # === PROMPT SIZE OPTIMIZATIONS ===
            # These optimizations reduce prompt size by ~50% to speed up LLM inference

            # 1. Filter mobs by distance (≤30 tiles) and remove unnecessary fields
            if "mobs" in enhanced_result:
                filtered_mobs = []
                for mob in enhanced_result["mobs"]:
                    distance = mob.get("distanceFrom", 999)
                    if distance <= 50:  # Only include nearby mobs
                        # Remove unnecessary fields to reduce size
                        filtered_mob = {
                            "instance": mob.get("instance"),  # Required for attack_entity
                            "name": mob.get("name"),
                            "level": mob.get("level"),
                            "x": mob.get("x"),
                            "y": mob.get("y"),
                            "hitPoints": mob.get("hitPoints"),
                            "maxHitPoints": mob.get("maxHitPoints"),
                            "aggressive": mob.get("aggressive"),
                            "distanceFrom": distance
                        }
                        filtered_mobs.append(filtered_mob)
                enhanced_result["mobs"] = filtered_mobs

            # 2. Aggregate inventory by item key and remove descriptions
            if "inventory" in enhanced_result and "items" in enhanced_result["inventory"]:
                items = enhanced_result["inventory"]["items"]
                aggregated = {}
                for item in items:
                    key = item.get("key", "unknown")
                    if key in aggregated:
                        aggregated[key]["count"] += item.get("count", 1)
                    else:
                        # Create compact item entry without description
                        aggregated[key] = {
                            "name": item.get("name"),
                            "count": item.get("count", 1),
                            "edible": item.get("edible", False),
                            "equippable": item.get("equippable", False)
                        }
                # Convert to list format
                enhanced_result["inventory"]["items"] = [
                    {"key": k, **v} for k, v in aggregated.items()
                ]

            # 3. Remove collision data (rarely needed, saves ~1KB)
            if "collisions" in enhanced_result:
                del enhanced_result["collisions"]

            # === END OPTIMIZATIONS ===

            # Store the raw observation data for logging
            self._last_observation_data = enhanced_result
            
            return f"Environment observation (radius {radius}): {json.dumps(enhanced_result, indent=2)}"
        else:
            return f"Failed to observe environment: {result.get('message', 'Unknown error')}"

    def enter_portal(self, arguments: Dict[str, Any]) -> str:
        """Enter a portal or warp point"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        data = {
            "token": self.token
        }
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["enter"], data)
        
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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["stop"], data)
        
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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["equip"], data)
        
        if result.get("status") == "success":
            item = result.get("item", {})
            return f"Item equipped successfully: {item.get('name', 'Unknown')} (type: {item.get('equipmentType', 'Unknown')})"
        else:
            return f"Failed to equip item: {result.get('message', 'Unknown error')}"

    def pickup_resource(self, arguments: Dict[str, Any]) -> str:
        """Pick up a dropped item or resource from the ground"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required for picking up items."
        
        data = {
            "token": self.token,
            "targetInstance": target_instance
        }
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["collect"], data)

        if result.get("status") == "success":
            resource = result.get("resource", {})
            return f"Picked up item: {resource.get('name', 'Unknown')} at ({resource.get('x')}, {resource.get('y')})"
        else:
            return f"Failed to pick up item: {result.get('message', 'Unknown error')}"

    def discard_item(self, arguments: Dict[str, Any]) -> str:
        """Discard (drop) an item from inventory to current location

        Drops an item from your inventory onto the ground at your current position.
        Other players can pick it up, or you can pick it back up later.

        Args:
            inventoryIndex: The inventory slot index of the item to discard (0-based)
            count: (optional) Number of items to discard if it's a stack. Default: all
        """
        if not self.token:
            return "Error: No token available. Please login first."

        inventory_index = arguments.get("inventoryIndex")
        count = arguments.get("count")

        if inventory_index is None:
            return "Error: inventoryIndex is required to discard an item."

        # First, check current inventory to validate the index
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"],
                                           params={"token": self.token, "radius": 1})

        if observe_result.get("status") != "success":
            return f"Error: Could not check inventory: {observe_result.get('message', 'Unknown error')}"

        inventory = observe_result.get("inventory", {}).get("items", [])

        if inventory_index < 0 or inventory_index >= len(inventory):
            return f"Error: Invalid inventory index {inventory_index}. You have {len(inventory)} items in inventory."

        item_to_discard = inventory[inventory_index]
        item_count = item_to_discard.get("count", 1)
        discard_count = count if count is not None else item_count

        if discard_count > item_count:
            return f"Error: Cannot discard {discard_count} items - you only have {item_count} of {item_to_discard.get('name', 'Unknown')}"

        # Use setInventory API to remove items from inventory
        # This will drop them on the ground at current location
        updated_inventory = []
        for i, item in enumerate(inventory):
            if i == inventory_index:
                remaining = item_count - discard_count
                if remaining > 0:
                    # Keep the remaining items
                    updated_item = item.copy()
                    updated_item["count"] = remaining
                    updated_inventory.append(updated_item)
                # else: don't add to updated inventory (fully discarded)
            else:
                updated_inventory.append(item)

        # Convert to API format
        api_items = []
        for item in updated_inventory:
            api_items.append({
                "key": item.get("key"),
                "count": item.get("count", 1)
            })

        data = {
            "token": self.token,
            "items": api_items,
            "clearFirst": True
        }

        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["setInventory"], data)

        if result.get("status") == "success":
            location = observe_result.get("location", {})
            return f"📦 Discarded {discard_count}x {item_to_discard.get('name', 'Unknown')} at position ({location.get('x')}, {location.get('y')}). You can pick it back up if needed."
        else:
            return f"Failed to discard item: {result.get('message', 'Unknown error')}"

    def destroy_item(self, arguments: Dict[str, Any]) -> str:
        """Permanently destroy an item from inventory

        Permanently removes an item from your inventory. This action cannot be undone.
        The item will NOT be dropped on the ground - it will be deleted completely.

        Args:
            inventoryIndex: The inventory slot index of the item to destroy (0-based)
            count: (optional) Number of items to destroy if it's a stack. Default: all
        """
        if not self.token:
            return "Error: No token available. Please login first."

        inventory_index = arguments.get("inventoryIndex")
        count = arguments.get("count")

        if inventory_index is None:
            return "Error: inventoryIndex is required to destroy an item."

        # First, check current inventory to validate the index
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"],
                                           params={"token": self.token, "radius": 1})

        if observe_result.get("status") != "success":
            return f"Error: Could not check inventory: {observe_result.get('message', 'Unknown error')}"

        inventory = observe_result.get("inventory", {}).get("items", [])

        if inventory_index < 0 or inventory_index >= len(inventory):
            return f"Error: Invalid inventory index {inventory_index}. You have {len(inventory)} items in inventory."

        item_to_destroy = inventory[inventory_index]
        item_count = item_to_destroy.get("count", 1)
        destroy_count = count if count is not None else item_count

        if destroy_count > item_count:
            return f"Error: Cannot destroy {destroy_count} items - you only have {item_count} of {item_to_destroy.get('name', 'Unknown')}"

        # Use setInventory API to remove items from inventory permanently
        updated_inventory = []
        for i, item in enumerate(inventory):
            if i == inventory_index:
                remaining = item_count - destroy_count
                if remaining > 0:
                    # Keep the remaining items
                    updated_item = item.copy()
                    updated_item["count"] = remaining
                    updated_inventory.append(updated_item)
                # else: don't add to updated inventory (destroyed)
            else:
                updated_inventory.append(item)

        # Convert to API format
        api_items = []
        for item in updated_inventory:
            api_items.append({
                "key": item.get("key"),
                "count": item.get("count", 1)
            })

        data = {
            "token": self.token,
            "items": api_items,
            "clearFirst": True
        }

        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["setInventory"], data)

        if result.get("status") == "success":
            return f"🗑️ Permanently destroyed {destroy_count}x {item_to_destroy.get('name', 'Unknown')} from inventory. This action cannot be undone."
        else:
            return f"Failed to destroy item: {result.get('message', 'Unknown error')}"

    def harvest_resource(self, arguments: Dict[str, Any]) -> str:
        """Harvest a resource using the appropriate skill (lumberjacking, mining, fishing, foraging)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required for resource collection."
        
        # First, get current environment to find the resource and determine its type
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 64})
        
        if observe_result.get("status") != "success":
            return f"Error: Could not observe environment to locate resource: {observe_result.get('message', 'Unknown error')}"
        
        # Log environment details for debugging
        env_info = [
            f"🌍 [ENVIRONMENT] Current environment observation:",
            f"   - Player location: {observe_result.get('location', {})}",
            f"   - Resources count: {len(observe_result.get('resources', []))}",
            f"   - Looking for instance: {target_instance}"
        ]
        
        # Print to console and log to file (only if debug enabled)
        for line in env_info:
            self._debug_print(line)
            self._log_message(line, "debug")
        
        # Find the resource in the raw resources array (our fixed API now returns resources here)
        resource_entity = None
        resource_type = None
        
        # Check in the raw resources array from the fixed API
        resources = observe_result.get("resources", [])
        for resource in resources:
            if resource.get("instance") == target_instance:
                resource_entity = resource
                # Determine type from the resource name
                name = resource.get("name", "").lower()
                if "tree" in name:
                    resource_type = "tree"
                elif "rock" in name:
                    resource_type = "rock"
                elif "fishing" in name or "fish" in name:
                    resource_type = "fishing spot"
                else:
                    resource_type = "foraging"  # Default for plants/foraging
                break
        
        if not resource_entity:
            error_lines = [
                f"❌ [RESOURCE ERROR] Resource with instance {target_instance} not found!",
                f"   - Available resources in environment:"
            ]
            for i, resource in enumerate(resources):
                error_lines.append(f"     [{i}] Instance: {resource.get('instance', 'N/A')}, Name: {resource.get('name', 'N/A')}, Position: ({resource.get('x', 'N/A')}, {resource.get('y', 'N/A')})")
            error_lines.extend([
                f"   - Total resources found: {len(resources)}",
                f"   - Requested instance: {target_instance}"
            ])
            
            # Print to console and log to file (only if debug enabled)
            for line in error_lines:
                self._debug_print(line)
                self._log_message(line, "error")
            
            return f"Error: Resource with instance {target_instance} not found in current environment. Found {len(resources)} resources total."
        
        resource_name = resource_entity.get("name", "Unknown")
        resource_x = resource_entity.get("x")
        resource_y = resource_entity.get("y")
        
        # Get player current position
        location = observe_result.get("location", {})
        player_x = location.get("x")
        player_y = location.get("y")
        
        if player_x is None or player_y is None:
            return "Error: Could not determine player position."
        
        # Calculate distance to resource using Manhattan distance (same as server)
        if resource_x is not None and resource_y is not None:
            distance = abs(resource_x - player_x) + abs(resource_y - player_y)
            
            # Move closer if too far (resources typically need to be within 2 tiles)
            if distance > 2:
                # Move to an adjacent position, not the exact resource location to avoid overlap
                if resource_x > player_x:
                    target_x = resource_x - 1  # Move one tile to the left of resource
                elif resource_x < player_x:
                    target_x = resource_x + 1  # Move one tile to the right of resource
                else:
                    target_x = resource_x
                    
                if resource_y > player_y:
                    target_y = resource_y - 1  # Move one tile above resource
                elif resource_y < player_y:
                    target_y = resource_y + 1  # Move one tile below resource
                else:
                    target_y = resource_y
                
                move_data = {
                    "token": self.token,
                    "x": target_x,
                    "y": target_y
                }
                
                move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], move_data)
                
                if move_result.get("status") != "success":
                    return f"Error: Failed to move closer to {resource_name}: {move_result.get('message', 'Unknown error')}"
                
                # IMPROVED POSITION SYNCHRONIZATION: Wait and verify position multiple times
                max_position_attempts = 5
                position_verified = False
                last_known_x, last_known_y = None, None

                for attempt in range(max_position_attempts):
                    # Progressive wait time: 2s, 2.5s, 3s, 3.5s, 4s (reduced for faster iteration)
                    wait_time = 2 + (attempt * 0.5)
                    time.sleep(wait_time)

                    # Verify the position update by checking current location (with inner retry for observe)
                    actual_x, actual_y = None, None
                    for observe_retry in range(3):  # Inner retry for observe API
                        current_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 1})
                        if current_observe.get("status") == "success":
                            # Note: observe API returns location directly, not under "data"
                            actual_x = current_observe.get("location", {}).get("x")
                            actual_y = current_observe.get("location", {}).get("y")
                            if actual_x is not None and actual_y is not None:
                                last_known_x, last_known_y = actual_x, actual_y
                                break
                        time.sleep(0.5)  # Short delay before observe retry

                    if actual_x is not None and actual_y is not None:
                        # Recalculate distance with actual position
                        actual_distance = abs(resource_x - actual_x) + abs(resource_y - actual_y)

                        # Position is good enough for harvesting
                        if actual_distance <= 2:
                            position_verified = True
                            movement_info = f"Moved closer to {resource_name} at ({resource_x}, {resource_y}) from position ({actual_x}, {actual_y}) (distance: {actual_distance}, attempt {attempt + 1}). "
                            break

                        # If still too far on the last attempt, try moving to exact resource location
                        elif attempt == max_position_attempts - 1:
                            exact_move_data = {
                                "token": self.token,
                                "x": resource_x,
                                "y": resource_y
                            }
                            exact_move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], exact_move_data)

                            # Final wait for exact position
                            time.sleep(2)

                            # Final position check with retry
                            for final_retry in range(3):
                                final_check = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 1})
                                if final_check.get("status") == "success":
                                    # Note: observe API returns location directly, not under "data"
                                    final_x = final_check.get("location", {}).get("x")
                                    final_y = final_check.get("location", {}).get("y")
                                    if final_x is not None and final_y is not None:
                                        final_distance = abs(resource_x - final_x) + abs(resource_y - final_y)
                                        if final_distance <= 2:
                                            position_verified = True
                                            movement_info = f"Moved to exact resource location {resource_name} at ({resource_x}, {resource_y}). Final position ({final_x}, {final_y}), distance: {final_distance}. "
                                        else:
                                            movement_info = f"Failed to get close enough to {resource_name}. Final distance: {final_distance}. "
                                        break
                                time.sleep(0.5)
                            else:
                                # Could not verify position, but proceed anyway as fallback
                                position_verified = True  # Allow harvest attempt
                                movement_info = f"Position verification uncertain for {resource_name}, proceeding with harvest attempt. "
                        else:
                            # Continue trying on intermediate attempts
                            self._debug_print(f"Position sync attempt {attempt + 1}: distance {actual_distance}, retrying...")
                            continue
                    else:
                        # Could not get position data, continue to next attempt
                        self._debug_print(f"Position sync attempt {attempt + 1}: could not get location data, retrying...")
                        if attempt == max_position_attempts - 1:
                            # On final attempt, proceed with harvest anyway (graceful degradation)
                            position_verified = True
                            movement_info = f"Position verification failed for {resource_name}, proceeding with harvest attempt anyway. "

                # If position was never verified after all attempts, still try harvest as last resort
                if not position_verified:
                    position_verified = True  # Allow harvest attempt as fallback
                    movement_info = f"Could not verify position for {resource_name}, attempting harvest anyway. "
            else:
                movement_info = f"Already near {resource_name}. "
        else:
            movement_info = ""
        
        # INSTANT HARVEST MODE: Complete the entire harvesting process immediately
        data = {
            "token": self.token,
            "targetInstance": target_instance
        }
        
        action_map = {
            "tree": "chopping",
            "rock": "mining", 
            "fishing spot": "fishing",
            "plant": "foraging"
        }
        action = action_map.get(resource_type, "collecting")
        
        # Get initial inventory state to track what items we gain
        initial_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 5})
        initial_inventory = {}
        if initial_observe.get("status") == "success":
            for item in initial_observe.get("inventory", {}).get("items", []):
                key = item.get("key", "")
                count = item.get("count", 0)
                if key:
                    initial_inventory[key] = initial_inventory.get(key, 0) + count
        
        # CRITICAL: Additional wait before starting skill to ensure movement has fully stopped
        # This prevents the skill from being interrupted by lingering movement effects
        time.sleep(2)  # Skill cooldown period
        
        # Final position verification before harvest - but only if we moved
        final_position_verified = False
        final_position_info = ""
        
        # If we didn't move (already near resource), skip strict verification
        if "Already near" in movement_info:
            # For already-near cases, do a simple verification with fallback
            simple_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 1})
            if simple_observe.get("status") == "success":
                # Note: observe API returns location directly, not under "data"
                simple_x = simple_observe.get("location", {}).get("x")
                simple_y = simple_observe.get("location", {}).get("y")
                
                if simple_x is not None and simple_y is not None and resource_x is not None and resource_y is not None:
                    simple_distance = abs(resource_x - simple_x) + abs(resource_y - simple_y)
                    final_position_info = f"Position check: Player at ({simple_x}, {simple_y}), Resource at ({resource_x}, {resource_y}), Distance: {simple_distance}. "
                    final_position_verified = True
                else:
                    # If coordinates are unavailable but we were already near, proceed anyway
                    final_position_info = f"Position coordinates unavailable, but agent was already near resource. Proceeding with harvest. "
                    final_position_verified = True
            else:
                # If observe fails but we were already near, proceed anyway
                final_position_info = f"Position verification unavailable, but agent was already near resource. Proceeding with harvest. "
                final_position_verified = True
        else:
            # For cases where we moved, do strict verification with retry mechanism
            for final_attempt in range(3):  # Try up to 3 times
                final_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 1})

                if final_observe.get("status") == "success":
                    # Note: observe API returns location directly, not under "data"
                    final_x = final_observe.get("location", {}).get("x")
                    final_y = final_observe.get("location", {}).get("y")
                    
                    if final_x is not None and final_y is not None and resource_x is not None and resource_y is not None:
                        final_distance = abs(resource_x - final_x) + abs(resource_y - final_y)
                        final_position_info = f"Final position verification (attempt {final_attempt + 1}): Player at ({final_x}, {final_y}), Resource at ({resource_x}, {resource_y}), Distance: {final_distance}. "
                        
                        # Position is acceptable for harvesting
                        if final_distance <= 2:
                            final_position_verified = True
                            break
                        else:
                            # If not the last attempt, wait and try again
                            if final_attempt < 2:
                                time.sleep(1)
                                continue
                            else:
                                return f"Error: {movement_info}{final_position_info}Cannot harvest - distance {final_distance} exceeds maximum allowed distance of 2 after {final_attempt + 1} verification attempts. This indicates a persistent server synchronization issue."
                    else:
                        final_position_info = f"Final position verification failed - could not get coordinates (attempt {final_attempt + 1}). "
                        if final_attempt < 2:
                            time.sleep(1)
                            continue
                else:
                    final_position_info = f"Final observation failed (attempt {final_attempt + 1}). "
                    if final_attempt < 2:
                        time.sleep(1)
                        continue
            
            # If we couldn't verify position after all attempts, abort
            if not final_position_verified:
                return f"Error: {movement_info}{final_position_info}Failed to verify position for harvest after multiple attempts."
        
        # Start the harvesting process with detailed logging
        debug_info = [
            f"🔍 [DEBUG] Attempting to harvest resource:",
            f"   - Resource Name: {resource_name}",
            f"   - Resource Type: {resource_type}",
            f"   - Target Instance: {target_instance}",
            f"   - Resource Position: ({resource_x}, {resource_y})",
            f"   - Player Position: ({player_x}, {player_y})",
            f"   - Distance: {distance if 'distance' in locals() else 'N/A'}",
            f"   - Action: {action}",
            f"   - API Endpoint: {AGENTWORLD_API_ENDPOINTS['collect']}",
            f"   - Request Data: {data}"
        ]
        
        # Print to console and log to file (only if debug enabled)
        for line in debug_info:
            self._debug_print(line)
            self._log_message(line, "debug")
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["collect"], data)
        
        response_info = [
            f"🔍 [DEBUG] Harvest API Response:",
            f"   - Status: {result.get('status', 'Unknown')}",
            f"   - Message: {result.get('message', 'No message')}",
            f"   - Full Response: {result}"
        ]
        
        # Print to console and log to file (only if debug enabled)
        for line in response_info:
            self._debug_print(line)
            self._log_message(line, "debug")
        
        if result.get("status") != "success":
            error_detail = f"API returned status '{result.get('status')}' with message: {result.get('message', 'Unknown error')}"
            error_msg = f"{movement_info}{final_position_info}Failed to start {action} {resource_name}: {error_detail}"
            
            # Log the error to file as well
            self._log_message(f"❌ HARVEST ERROR: {error_msg}", "error")
            
            return error_msg
        
        # ENHANCED MODE: Monitor the harvesting process until completion
        max_wait_time = 30  # Maximum wait time in seconds
        check_interval = 0.5  # Check every 500ms
        total_wait = 0
        harvested_items = []
        
        while total_wait < max_wait_time:
            # Small delay to let server process
            time.sleep(check_interval)
            total_wait += check_interval
            
            # Check current status
            current_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 10})
            
            if current_observe.get("status") == "success":
                # Check if the target resource still exists
                resource_still_exists = False
                current_resources = current_observe.get("resources", [])
                
                for res in current_resources:
                    if res.get("instance") == target_instance:
                        resource_still_exists = True
                        break
                
                # If resource is gone, harvesting is complete!
                if not resource_still_exists:
                    break
            
                # Track inventory changes during harvesting
                current_inventory = {}
                for item in current_observe.get("inventory", {}).get("items", []):
                    key = item.get("key", "")
                    count = item.get("count", 0)
                    if key:
                        current_inventory[key] = current_inventory.get(key, 0) + count
                
                # Check what items we gained so far
                for key, count in current_inventory.items():
                    initial_count = initial_inventory.get(key, 0)
                    if count > initial_count:
                        gained = count - initial_count
                        # Update existing entry or add new one
                        found = False
                        for item in harvested_items:
                            if item["key"] == key:
                                item["gained"] = gained
                                found = True
                                break
                        if not found:
                            harvested_items.append({"key": key, "name": key.title(), "gained": gained})
        
        # Final inventory check to see what we collected
        final_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 5})
        final_inventory = {}
        if final_observe.get("status") == "success":
            for item in final_observe.get("inventory", {}).get("items", []):
                key = item.get("key", "")
                count = item.get("count", 0)
                if key:
                    final_inventory[key] = final_inventory.get(key, 0) + count
        
        # Calculate all items gained during harvesting
        final_harvested_items = []
        for key, count in final_inventory.items():
            initial_count = initial_inventory.get(key, 0)
            if count > initial_count:
                gained = count - initial_count
                # Try to get proper item name from observation
                item_name = key.title()
                for item in final_observe.get("inventory", {}).get("items", []):
                    if item.get("key") == key:
                        item_name = item.get("name", key.title())
                        break
                final_harvested_items.append({"key": key, "name": item_name, "gained": gained})
        
        # Build comprehensive result message with detailed outcome
        if final_harvested_items:
            items_text = ", ".join([f"{item['gained']}x {item['name']}" for item in final_harvested_items])
            total_items = sum(item['gained'] for item in final_harvested_items)
            
            # Create detailed success message
            result_message = (
                f"{movement_info}✅ HARVEST COMPLETE: {action.title()} {resource_name} at ({resource_x}, {resource_y})\n"
                f"📦 Items Collected ({total_items} total): {items_text}\n"
                f"⚡ Process: Resource depleted and items automatically added to inventory\n"
                f"🎯 Status: Ready for next action"
            )
            
            # POST-HARVEST COOLDOWN: Wait to ensure skill completion is fully processed
            time.sleep(1.5)  # Brief cooldown after successful harvest
            
            return result_message
            
        elif total_wait >= max_wait_time:
            # POST-HARVEST COOLDOWN: Even for incomplete harvests
            time.sleep(1.5)
            
            return (
                f"{movement_info}⏳ HARVEST IN PROGRESS: {action.title()} {resource_name} at ({resource_x}, {resource_y})\n"
                f"📋 Status: Harvesting process started but may take additional time to complete\n"
                f"💡 Note: Check inventory periodically for collected items"
            )
        else:
            # POST-HARVEST COOLDOWN: For completed harvests without detected items
            time.sleep(1.5)
            
            return (
                f"{movement_info}✅ HARVEST COMPLETE: {action.title()} {resource_name} at ({resource_x}, {resource_y})\n"
                f"📦 Items Collected: Resource depleted (no items detected in inventory change)\n"
                f"⚡ Process: Resource successfully harvested\n"
                f"🎯 Status: Ready for next action"
            )

    def craft_item(self, arguments: Dict[str, Any]) -> str:
        """Craft an item using the specified crafting skill"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        skill = arguments.get("skill", "")
        item_key = arguments.get("itemKey", "")
        count = arguments.get("count", 1)
        
        if not skill:
            return "Error: Crafting skill is required."
        
        if not item_key:
            return "Error: Item key is required for crafting."
        
        # Validate skill type (based on actual Modules.Skills enum and API documentation)
        valid_skills = ["Crafting", "Smithing", "Fletching", "Cooking", "Smelting"]
        if skill not in valid_skills:
            return f"Error: Invalid skill '{skill}'. Must be one of: {', '.join(valid_skills)}"
        
        # Validate count (API only accepts 1, 5, or 10)
        if count not in [1, 5, 10]:
            return "Error: Count must be 1, 5, or 10."
        
        # Get current inventory before crafting for debugging
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 5})
        current_inventory = {}
        if observe_result.get("status") == "success":
            for item in observe_result.get("inventory", {}).get("items", []):
                key = item.get("key", "")
                count_inv = item.get("count", 0)
                if key:
                    current_inventory[key] = count_inv
        
        data = {
            "token": self.token,
            "type": skill,
            "itemKey": item_key,
            "count": count
        }
        
        # Debug information
        debug_info = [
            f"🔧 [CRAFT DEBUG] Attempting to craft item:",
            f"   - Skill: {skill}",
            f"   - Item Key: {item_key}",
            f"   - Count: {count}",
            f"   - Current Inventory: {current_inventory}",
            f"   - API Endpoint: {AGENTWORLD_API_ENDPOINTS['craft']}",
            f"   - Request Data: {data}"
        ]
        
        # Print to console and log to file (only if debug enabled)
        for line in debug_info:
            self._debug_print(line)
            self._log_message(line, "debug")
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["craft"], data)
        
        # Debug response information
        response_info = [
            f"🔧 [CRAFT DEBUG] API Response:",
            f"   - Status: {result.get('status', 'Unknown')}",
            f"   - Message: {result.get('message', 'No message')}",
            f"   - Full Response: {result}"
        ]
        
        # Print to console and log to file (only if debug enabled)
        for line in response_info:
            self._debug_print(line)
            self._log_message(line, "debug")
        
        if result.get("status") == "success":
            item_info = result.get("item", {})
            return f"Successfully crafted {count}x {item_info.get('name', item_key)}!"
        else:
            # Handle missing materials error with detailed information
            missing_materials = result.get("missingMaterials", [])
            requirements = result.get("requirements", [])
            required_level = result.get("requiredLevel")
            current_level = result.get("currentLevel")
            
            if missing_materials:
                missing_list = []
                for material in missing_materials:
                    missing_list.append(f"{material.get('name', material.get('key'))}: need {material.get('required')} but have {material.get('available')}")
                
                requirements_list = []
                for req in requirements:
                    requirements_list.append(f"{req.get('name', req.get('key'))}: {req.get('count')}")
                
                return (f"Failed to craft {item_key}: Missing materials!\n"
                       f"Required materials: {', '.join(requirements_list)}\n"
                       f"Missing: {', '.join(missing_list)}")
            elif required_level and current_level:
                return f"Failed to craft {item_key}: Level requirement not met! Need level {required_level} {skill}, but current level is {current_level}"
            else:
                return f"Failed to craft {item_key}: {result.get('message', 'Unknown error')}"

    def attack_entity(self, arguments: Dict[str, Any]) -> str:
        """Attack an entity directly by providing its instance ID.

        This method will automatically:
        1. Find the target entity in the current environment
        2. Move to an adjacent position (up/down/left/right) if not already adjacent
        3. Monitor combat until the mob dies or player dies (up to 60 seconds)
        4. Automatically collect any dropped items after victory

        Args:
            targetInstance: The instance ID of the entity to attack (from environment observation)
        """
        # Delegate to attack_mob which has proper combat monitoring
        # This ensures combat continues until completion (mob or player dies)
        return self.attack_mob(arguments)

    def attack_mob(self, arguments: Dict[str, Any]) -> str:
        """Enhanced combat function that completes entire battle until mob or player dies.
        
        This function automatically:
        1. Finds the target mob and moves to optimal attack position
        2. Monitors the entire combat process until completion
        3. Automatically collects all dropped items when mob dies
        4. Reports detailed outcome including items obtained and current HP/MP
        
        Args:
            targetInstance: The instance ID of the mob to attack (from environment observation)
        """
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required for combat."
        
        # Get initial state
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 64})
        
        if observe_result.get("status") != "success":
            return f"Error: Could not observe environment: {observe_result.get('message', 'Unknown error')}"
        
        # Find target mob
        mobs = observe_result.get("mobs", [])
        target_mob = None
        
        for mob in mobs:
            if mob.get("instance") == target_instance:
                target_mob = mob
                break
        
        if not target_mob:
            return f"Error: Target mob {target_instance} not found in current environment."
        
        # Get initial player status
        player_status = observe_result.get("playerStatus", {})
        initial_hp = player_status.get("hitPoints", 0)
        initial_max_hp = player_status.get("maxHitPoints", 0)
        initial_mp = player_status.get("mana", 0)
        initial_max_mp = player_status.get("maxMana", 0)
        
        # Get initial inventory for tracking drops
        initial_inventory = {}
        for item in observe_result.get("inventory", {}).get("items", []):
            key = item.get("key", "")
            count = item.get("count", 0)
            if key:
                initial_inventory[key] = initial_inventory.get(key, 0) + count
        
        # Check if player has a ranged weapon equipped (bow, staff, etc.)
        equipped_items = observe_result.get("inventory", {}).get("equipped", [])
        is_ranged_weapon = False
        attack_range = 1  # Default melee range
        
        # Debug: Log equipped items to help diagnose detection issues
        self._log_message(f"🔍 Checking equipped items for ranged weapons: {equipped_items}", "debug")
        
        for equip in equipped_items:
            equip_key = equip.get("key", "").lower()
            # Check attackStyle/attackRange from equipment data (server provides this for ranged weapons)
            equip_attack_range = equip.get("attackRange", equip.get("attackStyle"pyt, 0))
            
            # Check for bow weapons or any weapon with attack range > 1
            if "bow" in equip_key or equip_attack_range > 1:
                is_ranged_weapon = True
                # Use the weapon's attack range if provided, otherwise default to archer range
                attack_range = equip_attack_range if equip_attack_range > 1 else 8
                self._log_message(f"🏹 Detected ranged weapon: {equip_key} with attack range {attack_range}", "debug")
                break
            # Also check for magic staves (ranged magic attacks)
            elif "staff" in equip_key:
                is_ranged_weapon = True
                attack_range = equip_attack_range if equip_attack_range > 1 else 6  # Magic staff default range
                self._log_message(f"🪄 Detected magic staff: {equip_key} with attack range {attack_range}", "debug")
                break
        
        if not is_ranged_weapon:
            self._log_message(f"⚔️ Using melee attack (no ranged weapon detected)", "debug")
        
        # Extract positions
        location = observe_result.get("location", {})
        player_x, player_y = location.get("x"), location.get("y")
        target_x, target_y = target_mob.get("x"), target_mob.get("y")
        target_name = target_mob.get("name", "Unknown")
        target_level = target_mob.get("level", "?")
        
        if any(v is None for v in [player_x, player_y, target_x, target_y]):
            return "Error: Could not determine positions."
        
        # Calculate distance to target
        dx, dy = abs(target_x - player_x), abs(target_y - player_y)
        distance = dx + dy  # Manhattan distance
        is_in_range = distance <= attack_range
        movement_info = ""
        
        if not is_in_range:
            # Need to move closer - but only close enough for our weapon range
            if is_ranged_weapon:
                # For ranged weapons, move to a position within range but not necessarily adjacent
                # Try to stay at optimal range (about half the max range)
                optimal_range = max(1, attack_range // 2)
                # Find a position that's about optimal_range tiles away from target
                possible_positions = []
                for ox in range(-optimal_range, optimal_range + 1):
                    for oy in range(-optimal_range, optimal_range + 1):
                        if abs(ox) + abs(oy) <= optimal_range and abs(ox) + abs(oy) > 0:
                            possible_positions.append((target_x + ox, target_y + oy))
                if not possible_positions:
                    # Fallback to adjacent positions
                    possible_positions = [
                        (target_x, target_y - 1), (target_x, target_y + 1),
                        (target_x - 1, target_y), (target_x + 1, target_y)
                    ]
            else:
                # For melee weapons, must be adjacent
                possible_positions = [
                    (target_x, target_y - 1), (target_x, target_y + 1),
                    (target_x - 1, target_y), (target_x + 1, target_y)
                ]
            
            best_position = min(possible_positions, 
                              key=lambda pos: abs(pos[0] - player_x) + abs(pos[1] - player_y))
            
            move_data = {"token": self.token, "x": best_position[0], "y": best_position[1]}
            move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], move_data)
            
            if move_result.get("status") != "success":
                return f"Error: Failed to move to attack position: {move_result.get('message', 'Unknown error')}"
            
            movement_info = f"Moved from ({player_x}, {player_y}) to {best_position} to attack {target_name}. "
            time.sleep(0.5)  # Position sync

            # Re-observe after moving to get fresh entity data (fixes region transition issues)
            observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"],
                                                params={"token": self.token, "radius": 64})
            if observe_result.get("status") != "success":
                return f"{movement_info}Error: Could not re-observe after move: {observe_result.get('message', 'Unknown error')}"

            # Re-validate target still exists after move
            mobs = observe_result.get("mobs", [])
            target_mob = None
            for mob in mobs:
                if mob.get("instance") == target_instance:
                    target_mob = mob
                    break

            if not target_mob:
                # Target no longer visible - might have died or moved out of range
                return f"{movement_info}Error: Target {target_name} (instance {target_instance}) no longer visible after moving. It may have been killed or moved away."

            # Update target position in case it moved
            target_x, target_y = target_mob.get("x"), target_mob.get("y")
            last_known_mob_x = target_x
            last_known_mob_y = target_y
        else:
            movement_info = f"Already adjacent to {target_name}. "

        # Initiate combat
        attack_data = {"token": self.token, "targetInstance": target_instance}
        attack_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["attack"], attack_data)
        
        if attack_result.get("status") != "success":
            return f"{movement_info}Failed to start combat: {attack_result.get('message', 'Unknown error')}"
        
        # ENHANCED COMBAT MONITORING - Fight until death (mob or player)
        check_interval = 0.5  # Check every 500ms
        total_time = 0
        max_combat_time = 1200  # Maximum 5 minutes per combat - prevents infinite loops
        combat_outcome = "unknown"
        final_hp = initial_hp
        final_mp = initial_mp
        re_attack_count = 0  # Track re-attack attempts
        last_known_mob_x = target_x  # Track mob's last known position for loot collection
        last_known_mob_y = target_y
        player_dealt_damage = False  # Track if THIS player actually participated in combat

        # Combat loop with timeout
        while total_time < max_combat_time:
            time.sleep(check_interval)
            total_time += check_interval

            # Check current battle status
            current_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"],
                                               params={"token": self.token, "radius": 32})

            if current_observe.get("status") == "success":
                # Check if player is still alive
                current_player_status = current_observe.get("playerStatus", {})
                final_hp = current_player_status.get("hitPoints", 0)
                final_mp = current_player_status.get("mana", 0)
                player_in_combat = current_player_status.get("combat", False)

                # If player is in combat, they are participating
                if player_in_combat:
                    player_dealt_damage = True

                if final_hp <= 0:
                    combat_outcome = "player_died"
                    break

                # Check if target mob still exists and update its position
                current_mobs = current_observe.get("mobs", [])
                target_mob_current = None
                for mob in current_mobs:
                    if mob.get("instance") == target_instance:
                        target_mob_current = mob
                        # Update last known position (mob's death position for loot)
                        last_known_mob_x = mob.get("x", last_known_mob_x)
                        last_known_mob_y = mob.get("y", last_known_mob_y)
                        break

                target_still_alive = target_mob_current is not None

                # SAFEGUARD: Check distance to target - if too far, something is wrong
                if target_still_alive:
                    current_loc = current_observe.get("location", {})
                    curr_player_x, curr_player_y = current_loc.get("x"), current_loc.get("y")
                    mob_x, mob_y = target_mob_current.get("x"), target_mob_current.get("y")
                    
                    if curr_player_x is not None and mob_x is not None:
                        distance_to_target = abs(mob_x - curr_player_x) + abs(mob_y - curr_player_y)
                        
                        # If player is beyond their weapon range + buffer, combat state is invalid
                        # Use attack_range + 3 as the max distance before breaking
                        max_combat_distance = attack_range + 3
                        if distance_to_target > max_combat_distance:
                            self._log_message(f"⚠️ Player too far from target ({distance_to_target} tiles, max {max_combat_distance}) - breaking combat loop", "warning")
                            combat_outcome = "distance_exceeded"
                            break

                if not target_still_alive:
                    # Mob is no longer in the environment - confirmed kill
                    # Count as victory if player participated (was in combat, took damage, or killed quickly)
                    hp_decreased = final_hp < initial_hp
                    if player_dealt_damage or hp_decreased or total_time < 3:
                        combat_outcome = "mob_died"
                    else:
                        combat_outcome = "mob_died_by_others"
                    break

                # If not in combat but mob still alive, re-engage combat immediately
                if not player_in_combat and total_time > 2 and target_still_alive:
                    # Check if we need to move closer to the mob (it may have moved)
                    current_loc = current_observe.get("location", {})
                    curr_player_x, curr_player_y = current_loc.get("x"), current_loc.get("y")
                    mob_x, mob_y = target_mob_current.get("x"), target_mob_current.get("y")

                    if curr_player_x is not None and mob_x is not None:
                        current_distance = abs(mob_x - curr_player_x) + abs(mob_y - curr_player_y)
                        is_in_attack_range = current_distance <= attack_range

                        if not is_in_attack_range:
                            # Move closer - use appropriate range based on weapon type
                            if is_ranged_weapon:
                                # For ranged, move to optimal range (not necessarily adjacent)
                                optimal_range = max(1, attack_range // 2)
                                possible_positions = []
                                for ox in range(-optimal_range, optimal_range + 1):
                                    for oy in range(-optimal_range, optimal_range + 1):
                                        if 0 < abs(ox) + abs(oy) <= optimal_range:
                                            possible_positions.append((mob_x + ox, mob_y + oy))
                                if not possible_positions:
                                    possible_positions = [(mob_x, mob_y - 1), (mob_x, mob_y + 1), (mob_x - 1, mob_y), (mob_x + 1, mob_y)]
                            else:
                                # For melee, must be adjacent
                                possible_positions = [(mob_x, mob_y - 1), (mob_x, mob_y + 1), (mob_x - 1, mob_y), (mob_x + 1, mob_y)]
                            
                            best_pos = min(possible_positions, key=lambda p: abs(p[0] - curr_player_x) + abs(p[1] - curr_player_y))
                            move_data = {"token": self.token, "x": best_pos[0], "y": best_pos[1]}
                            self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], move_data)
                            time.sleep(0.3)
                            # Update last known position
                            last_known_mob_x, last_known_mob_y = mob_x, mob_y

                    # Re-initiate attack on the still-alive mob
                    re_attack_data = {"token": self.token, "targetInstance": target_instance}
                    re_attack_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["attack"], re_attack_data)
                    re_attack_count += 1
                    self._log_message(f"⚔️ Re-engaging {target_name} (attempt {re_attack_count})", "debug")

                    # If attack failed, stop trying - target may have moved or died
                    if re_attack_result.get("status") != "success":
                        error_msg = re_attack_result.get("message", "")
                        self._log_message(f"🎯 Re-attack failed: {error_msg} - stopping combat loop", "debug")
                        # Check if player participated before marking as team kill
                        hp_decreased = final_hp < initial_hp
                        if player_dealt_damage or hp_decreased:
                            combat_outcome = "mob_died"
                        else:
                            combat_outcome = "mob_died_by_others"
                        break
        
        # Handle combat timeout
        if combat_outcome == "unknown" and total_time >= max_combat_time:
            self._log_message(f"⚠️ Combat timed out after {max_combat_time}s - breaking combat loop", "warning")
            combat_outcome = "timeout"
        
        # IMPROVED Auto-collect dropped items if mob died - now using groundItems and pickup API
        # Any agent can loot regardless of who got the killing blow
        collected_items = []

        if combat_outcome in ("mob_died", "mob_died_by_others"):
            # Move to mob's LAST KNOWN position (death location) to collect drops
            pickup_move_data = {"token": self.token, "x": last_known_mob_x, "y": last_known_mob_y}
            pickup_move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], pickup_move_data)
            print(f"[LOOT DEBUG] Moving to loot at ({last_known_mob_x}, {last_known_mob_y}) - mob's death location")
            print(f"[LOOT DEBUG] Move result: {pickup_move_result}")

            if pickup_move_result.get("status") == "success":
                # Wait for items to drop and server processing
                time.sleep(1.5)

                # Multiple collection attempts for better reliability
                for attempt in range(3):
                    # Observe ground items at the loot location
                    loot_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"],
                                                      params={"token": self.token, "radius": 10})

                    print(f"[LOOT DEBUG] Attempt {attempt+1}: Observe status={loot_observe.get('status')}")

                    if loot_observe.get("status") == "success":
                        # Get ground items from observation
                        ground_items = loot_observe.get("groundItems", [])
                        player_loc = loot_observe.get("location", {})
                        print(f"[LOOT DEBUG] Player location: ({player_loc.get('x')}, {player_loc.get('y')})")
                        print(f"[LOOT DEBUG] Ground items found: {len(ground_items)}")
                        print(f"[LOOT DEBUG] Ground items data: {ground_items}")

                        if ground_items:
                            self._log_message(f"🎁 Found {len(ground_items)} ground items to collect", "debug")

                            # Try to pick up each ground item
                            for ground_item in ground_items:
                                item_instance = ground_item.get("instance", "")
                                item_name = ground_item.get("name", "Unknown")
                                item_count = ground_item.get("count", 1)
                                item_distance = ground_item.get("distanceFrom", 0)

                                # Only try to pick up items that are close enough
                                if item_distance <= 2:
                                    pickup_result = self._make_request(
                                        "POST",
                                        AGENTWORLD_API_ENDPOINTS["pickup"],
                                        {"token": self.token, "targetInstance": item_instance}
                                    )

                                    if pickup_result.get("status") == "success":
                                        collected_items.append({
                                            "key": ground_item.get("key", ""),
                                            "name": item_name,
                                            "count": item_count
                                        })
                                        self._log_message(f"✅ Picked up {item_count}x {item_name}", "debug")
                                    else:
                                        error_msg = pickup_result.get("message", "")
                                        self._log_message(f"❌ Failed to pick up {item_name}: {error_msg}", "debug")
                                else:
                                    # Item too far, try to move closer
                                    item_x = ground_item.get("x", last_known_mob_x)
                                    item_y = ground_item.get("y", last_known_mob_y)
                                    self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"],
                                                      {"token": self.token, "x": item_x, "y": item_y})
                                    time.sleep(0.5)

                            # If we collected items, we're done
                            if collected_items:
                                break
                        else:
                            print(f"[LOOT DEBUG] 📭 No ground items found at loot location (attempt {attempt + 1})")
                    else:
                        print(f"[LOOT DEBUG] Observe failed: {loot_observe}")

                    # Brief wait before next attempt
                    if attempt < 2 and not collected_items:
                        time.sleep(1.0)
            else:
                print(f"[LOOT DEBUG] Move to loot location failed: {pickup_move_result}")
        
        # Build comprehensive result message
        hp_change = final_hp - initial_hp
        mp_change = final_mp - initial_mp
        
        if combat_outcome == "mob_died":
            if collected_items:
                items_text = ", ".join([f"{item['count']}x {item['name']}" for item in collected_items])
                loot_note = f"🎁 Loot Collected: {items_text}"
            else:
                # Note about drop rates for user understanding
                loot_note = f"🎁 Loot Collected: No items collected this time"
            
            result_message = (
                f"{movement_info}🏆 VICTORY: Defeated {target_name} (Level {target_level})\n"
                f"💀 Enemy Status: {target_name} eliminated\n"
                f"{loot_note}\n"
                f"❤️  Player HP: {final_hp}/{initial_max_hp} ({hp_change:+d})\n"
                f"💙 Player MP: {final_mp}/{initial_max_mp} ({mp_change:+d})\n"
                f"⚡ Combat Duration: {total_time:.1f}s\n"
                f"🎯 Status: Ready for next action"
            )
        
        elif combat_outcome == "player_died":
            result_message = (
                f"{movement_info}💀 DEFEAT: You were slain by {target_name} (Level {target_level})\n"
                f"❤️  Player HP: 0/{initial_max_hp} (DEAD)\n"
                f"💙 Player MP: {final_mp}/{initial_max_mp}\n"
                f"⚡ Combat Duration: {total_time:.1f}s\n"
                f"⚠️  Status: Respawn required"
            )
        
        elif combat_outcome == "mob_died_by_others":
            # Mob was killed by another agent - but we can still loot
            if collected_items:
                items_text = ", ".join([f"{item['count']}x {item['name']}" for item in collected_items])
                loot_note = f"🎁 Loot Collected: {items_text}"
            else:
                loot_note = f"🎁 Loot Collected: No items collected this time"

            result_message = (
                f"{movement_info}👥 VICTORY (Team Kill): {target_name} (Level {target_level}) was defeated\n"
                f"{loot_note}\n"
                f"❤️  Player HP: {final_hp}/{initial_max_hp} ({hp_change:+d})\n"
                f"💙 Player MP: {final_mp}/{initial_max_mp} ({mp_change:+d})\n"
                f"⚡ Combat Duration: {total_time:.1f}s\n"
                f"🎯 Status: Target eliminated - ready for next action"
            )

        elif combat_outcome == "distance_exceeded":
            # Player got too far from target - combat state was invalid
            result_message = (
                f"{movement_info}⚠️ COMBAT INTERRUPTED: Too far from {target_name} (Level {target_level})\n"
                f"❤️  Player HP: {final_hp}/{initial_max_hp} ({hp_change:+d})\n"
                f"💙 Player MP: {final_mp}/{initial_max_mp} ({mp_change:+d})\n"
                f"⚡ Time Elapsed: {total_time:.1f}s\n"
                f"🎯 Status: Combat ended - player too far from target. Move closer and try again."
            )

        elif combat_outcome == "timeout":
            # Combat took too long - break out to prevent infinite loops
            result_message = (
                f"{movement_info}⏱️ COMBAT TIMEOUT: Battle with {target_name} (Level {target_level}) took too long\n"
                f"❤️  Player HP: {final_hp}/{initial_max_hp} ({hp_change:+d})\n"
                f"💙 Player MP: {final_mp}/{initial_max_mp} ({mp_change:+d})\n"
                f"⚡ Time Elapsed: {total_time:.1f}s (max: {max_combat_time}s)\n"
                f"🎯 Status: Combat timed out. Target may still be alive - try attacking again or find another target."
            )

        else:
            # This should rarely happen - combat ended without clear outcome
            result_message = (
                f"{movement_info}❓ COMBAT ENDED: Battle with {target_name} (Level {target_level})\n"
                f"❤️  Player HP: {final_hp}/{initial_max_hp} ({hp_change:+d})\n"
                f"💙 Player MP: {final_mp}/{initial_max_mp} ({mp_change:+d})\n"
                f"⚡ Combat Duration: {total_time:.1f}s\n"
                f"🔄 Re-attack Attempts: {re_attack_count}\n"
                f"📋 Status: Outcome unclear"
            )

        return result_message

    def set_combat_level(self, arguments: Dict[str, Any]) -> str:
        """Set combat level by adjusting all combat skills"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        level = arguments.get("level")
        
        if level is None:
            return "Error: Level is required."
        
        level = int(level)
        if level < 1 or level > 120:
            return "Error: Level must be between 1 and 120."
        
        data = {
            "token": self.token,
            "level": level
        }
        
        # Use the dedicated AI endpoint for setting combat level
        result = self._make_request("POST", "/ai/setCombatLevel", data)
        
        if result.get("status") == "success":
            updates = result.get("updates", [])
            combat_level = result.get("combatLevel", {})
            updates_str = "\n".join(updates)
            return f"Combat level updated successfully!\n{updates_str}\nTotal Combat Level: {combat_level.get('actual', 'Unknown')}"
        else:
            return f"Failed to set combat level: {result.get('message', 'Unknown error')}"

    def give_and_equip_item(self, arguments: Dict[str, Any]) -> str:
        """Give and equip an item (admin cheat command)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        item_key = arguments.get("itemKey", "")
        count = arguments.get("count", 1)
        enchantment_level = arguments.get("enchantmentLevel", 0)
        
        if not item_key:
            return "Error: Item key is required."
        
        # Create enchantments object if enchantment level is specified
        enchantments = {}
        if enchantment_level > 0:
            # Common enchantment types in Kaetram
            enchantments = {
                "damage": enchantment_level,
                "accuracy": enchantment_level,
                "defense": enchantment_level
            }
        
        # Try to determine equipment type from item key
        equipment_type = self._guess_equipment_type(item_key)
        
        if equipment_type:
            # Use setEquipments endpoint to directly equip the item
            equipment_data = {
                "token": self.token,
                "equipment": {
                    equipment_type: {
                        "key": item_key,
                        "count": int(count),
                        "enchantments": enchantments
                    }
                },
                "clearFirst": False  # Don't clear other equipment
            }
            
            result = self._make_request("POST", "/ai/setEquipments", equipment_data)
            
            if result.get("status") == "success":
                enchant_text = f" +{enchantment_level}" if enchantment_level > 0 else ""
                return f"Successfully equipped {count}x {item_key}{enchant_text}"
            else:
                return f"Failed to equip item: {result.get('message', 'Unknown error')}"
        else:
            # If we can't determine equipment type, add to inventory instead
            inventory_data = {
                "token": self.token,
                "items": [{
                    "key": item_key,
                    "count": int(count),
                    "enchantments": enchantments
                }],
                "clearFirst": False  # Don't clear existing inventory
            }
            
            result = self._make_request("POST", "/ai/setInventory", inventory_data)
            
            if result.get("status") == "success":
                enchant_text = f" +{enchantment_level}" if enchantment_level > 0 else ""
                return f"Successfully added {count}x {item_key}{enchant_text} to inventory"
            else:
                return f"Failed to add item: {result.get('message', 'Unknown error')}"

    def set_player_level(self, arguments: Dict[str, Any]) -> str:
        """Set player level (admin cheat command)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_level = arguments.get("level", 1)
        
        if target_level < 1 or target_level > 120:
            return "Error: Level must be between 1 and 120."
        
        # Try the new setCombatLevel endpoint first
        data = {
            "token": self.token,
            "level": int(target_level)
        }
        
        result = self._make_request("POST", "/ai/setCombatLevel", data)
        
        if result.get("status") == "success":
            combat_level = result.get("combatLevel", {})
            actual_level = combat_level.get("actual", target_level)
            skill_updates = result.get("updates", [])
            
            return f"Successfully set all combat skills to level {target_level}. Total combat level: {actual_level}"
        else:
            # Fallback to the old method if new endpoint doesn't exist
            fallback_data = {
                "token": self.token,
                "level": int(target_level)
            }
            
            fallback_result = self._make_request("POST", "/ai/setPlayerStatus", fallback_data)
            
            if fallback_result.get("status") == "success":
                current_status = fallback_result.get("currentStatus", {})
                new_level = current_status.get("level", target_level)
                return f"⚠️ Set internal level to {new_level}, but display level is calculated from combat skills. Use combat training to increase actual level."
            else:
                return f"Failed to set level: {result.get('message', 'Unknown error')}"

    def give_full_equipment(self, arguments: Dict[str, Any]) -> str:
        """Give player a full set of equipment (admin cheat command)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        # Essential equipment set suitable for level 45 - verified valid item keys
        equipment_set = [
            # Weapons - variety of types for different playstyles
            {"key": "bastardsword", "count": 1},          # Heavy Sword (Level 40) [bigsword]
            {"key": "cactusaxe", "count": 1},             # Cactus Axe (Level 36) [axe]
            {"key": "trident", "count": 1},               # Trident Of The Seas (Level 40) [spear]
            {"key": "whip", "count": 1},                  # Whip (Level 50) [whip]
            
            # Archer weapons
            {"key": "rosebow", "count": 1},               # Rose Bow (Level 50) [bow]
            {"key": "hunterbow", "count": 1},             # Hunter Bow (Level 37) [bow]
            
            # Magic weapons
            {"key": "icestaff", "count": 1},              # Ice Staff (Level 35) [staff]
            {"key": "firestaff", "count": 1},             # Fire Staff (Level 25) [staff]
            
            # Armor pieces
            {"key": "whitearmor", "count": 1},            # White Armour (Level 46)
            {"key": "redguardarmor", "count": 1},         # Red Guard Armour (Level 40)
            
            # Boots
            {"key": "lavaboots", "count": 1},             # Lava Boots (Level 0)
            {"key": "goldboots", "count": 1},             # Golden Boots (Level 0)
            
            # Accessories
            {"key": "pytharring", "count": 1},            # Pythar Ring (Level 50)
            {"key": "emeraldring", "count": 1},           # Emerald Ring (Level 30)
            {"key": "emeraldpendant", "count": 1},        # Emerald Pendant (Level 0)
            {"key": "rubypendant", "count": 1},           # Ruby Pendant (Level 0)
            
            # Arrows for archer builds
            {"key": "pythararrow", "count": 100},         # Pythar Arrow (Level 0)
            {"key": "firearrow", "count": 100},           # Fire Arrow (Level 0)
        ]
        
        # Use the existing setInventory endpoint to add all items to inventory
        data = {
            "token": self.token,
            "items": equipment_set,
            "clearFirst": False  # Don't clear existing inventory
        }
        
        result = self._make_request("POST", "/ai/setInventory", data)
        
        if result.get("status") == "success":
            results = result.get("results", {})
            added_items = results.get("addedItems", [])
            failed_items = results.get("failedItems", [])
            
            success_count = len(added_items)
            total_count = len(equipment_set)
            
            message = f"Successfully added {success_count}/{total_count} equipment items to inventory"
            
            if failed_items:
                failed_names = [item.get("key", "unknown") for item in failed_items]
                message += f". Failed items: {', '.join(failed_names)}"
            
            return message
        else:
            return f"Failed to give equipment: {result.get('message', 'Unknown error')}"

    def _guess_equipment_type(self, item_key: str) -> Optional[str]:
        """Guess equipment type from item key for auto-equipping"""
        item_key_lower = item_key.lower()
        
        # Weapon patterns (includes fishingpole which is equipped as weapon for fishing)
        if any(weapon in item_key_lower for weapon in ['sword', 'bow', 'staff', 'dagger', 'axe', 'mace', 'spear', 'fishingpole', 'pole']):
            return 'weapon'
        
        # Helmet patterns
        if any(helmet in item_key_lower for helmet in ['helmet', 'hat', 'cap', 'crown', 'hood']):
            return 'helmet'
        
        # Chestplate patterns
        if any(chest in item_key_lower for chest in ['chestplate', 'armor', 'armour', 'tunic', 'robe', 'shirt']):
            return 'chestplate'
        
        # Shield patterns
        if any(shield in item_key_lower for shield in ['shield', 'buckler']):
            return 'shield'
        
        # Boots patterns
        if any(boots in item_key_lower for boots in ['boots', 'shoes', 'sandals', 'slippers']):
            return 'boots'
        
        # Legplates patterns
        if any(legs in item_key_lower for legs in ['legplates', 'pants', 'leggings', 'greaves']):
            return 'legplates'
        
        # Cape patterns
        if any(cape in item_key_lower for cape in ['cape', 'cloak', 'mantle']):
            return 'cape'
        
        # Ring patterns
        if any(ring in item_key_lower for ring in ['ring']):
            return 'ring'
        
        # Pendant patterns
        if any(pendant in item_key_lower for pendant in ['pendant', 'necklace', 'amulet']):
            return 'pendant'
        
        # Arrows patterns
        if any(arrow in item_key_lower for arrow in ['arrow', 'bolt']):
            return 'arrows'
        
        return None  # Can't determine equipment type, will add to inventory instead

    def sleep(self, arguments: Dict[str, Any]) -> str:
        """Sleep for specified number of seconds"""
        import time
        
        seconds = arguments.get("seconds", 1)
        
        try:
            seconds = int(seconds)
            if seconds < 1:
                seconds = 1
            elif seconds > 60:
                seconds = 60
                
            time.sleep(seconds)
            return f"Slept for {seconds} second(s)."
        except Exception as e:
            return f"Error: Could not sleep: {str(e)}"

    def check_inventory_status(self, arguments: Dict[str, Any]) -> str:
        """Check current inventory status without any requirements - use this before making any inventory claims"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        # Get current inventory with double verification
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], 
                                          params={"token": self.token, "radius": 5})
        time.sleep(0.3)
        verify_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], 
                                         params={"token": self.token, "radius": 5})
        
        if observe_result.get("status") != "success":
            return f"Error: Could not observe inventory: {observe_result.get('message', 'Unknown error')}"
        
        # Use the second verification result for reliability
        if verify_result.get("status") == "success":
            inventory = verify_result.get("inventory", {}).get("items", [])
        else:
            inventory = observe_result.get("inventory", {}).get("items", [])
        
        # Count all items in inventory
        inventory_counts = {}
        for item in inventory:
            key = item.get("key", "")
            count = item.get("count", 0)
            if key and count > 0:
                inventory_counts[key] = inventory_counts.get(key, 0) + count
        
        # Format inventory status
        if inventory_counts:
            items_list = []
            for key, count in inventory_counts.items():
                items_list.append(f"{key} ({count}x)")
            return f"🎒 CURRENT INVENTORY: {', '.join(items_list)}"
        else:
            return "🎒 CURRENT INVENTORY: EMPTY - No items in inventory"

    def verify_inventory(self, arguments: Dict[str, Any]) -> str:
        """Verify that specific items are in inventory before proceeding"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        required_items = arguments.get("required_items", [])
        
        if not required_items:
            return "Error: No required items specified for verification."
        
        # Get current inventory with increased reliability
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], 
                                          params={"token": self.token, "radius": 5})
        
        # Add a second verification call to ensure consistency
        time.sleep(0.5)  # Brief delay for server sync
        verify_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], 
                                         params={"token": self.token, "radius": 5})
        
        if observe_result.get("status") != "success":
            return f"Error: Could not observe inventory: {observe_result.get('message', 'Unknown error')}"
        
        # Use the second verification result for consistency check
        if verify_result.get("status") == "success":
            inventory = verify_result.get("inventory", {}).get("items", [])
        else:
            inventory = observe_result.get("inventory", {}).get("items", [])
        
        # Check each required item
        inventory_counts = {}
        for item in inventory:
            key = item.get("key", "")
            count = item.get("count", 0)
            if key:
                inventory_counts[key] = inventory_counts.get(key, 0) + count
        
        missing_items = []
        present_items = []
        
        for required_item in required_items:
            if required_item in inventory_counts and inventory_counts[required_item] > 0:
                present_items.append(f"{required_item} ({inventory_counts[required_item]}x)")
            else:
                missing_items.append(required_item)
        
        # Show complete inventory for transparency
        all_items = []
        for key, count in inventory_counts.items():
            all_items.append(f"{key} ({count}x)")
        
        # Prepare verification result
        result_lines = ["📋 INVENTORY VERIFICATION:"]
        result_lines.append(f"🎒 Complete Inventory: {', '.join(all_items) if all_items else 'EMPTY'}")
        
        if present_items:
            result_lines.append(f"✅ Present: {', '.join(present_items)}")
        
        if missing_items:
            result_lines.append(f"❌ Missing: {', '.join(missing_items)}")
            result_lines.append("⚠️ Cannot proceed with crafting until all materials are obtained!")
            return "\n".join(result_lines)
        else:
            result_lines.append("✅ All required materials are present in inventory!")
            result_lines.append("🔨 Ready to proceed with crafting!")
            return "\n".join(result_lines)

    def complete(self, arguments: Dict[str, Any]) -> str:
        """Complete the current task with a final response"""
        response = arguments.get("response", "Task completed.")
        
        if not response or not isinstance(response, str):
            response = "Task completed."
            
        return f"TASK_COMPLETE: {response}" 

    def set_individual_skill_level(self, arguments: Dict[str, Any]) -> str:
        """Set individual skill level (admin cheat command)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        skill = arguments.get("skill", "")
        level = arguments.get("level", 1)
        
        if not skill:
            return "Error: Skill name is required."
        
        if level < 1 or level > 120:
            return "Error: Level must be between 1 and 120."
        
        # Map skill names to proper casing
        skill_mapping = {
            "accuracy": "Accuracy",
            "strength": "Strength", 
            "defense": "Defense",
            "health": "Health",
            "magic": "Magic",
            "archery": "Archery",
            "lumberjacking": "Lumberjacking",
            "mining": "Mining",
            "fishing": "Fishing",
            "cooking": "Cooking",
            "smithing": "Smithing",
            "crafting": "Crafting",
            "fletching": "Fletching",
            "foraging": "Foraging"
        }
        
        skill_proper = skill_mapping.get(skill.lower(), skill)
        
        # Log the skill setting attempt for debugging
        self._log_message(f"🔧 Setting skill {skill_proper} to level {level}", "debug")
        
        data = {
            "token": self.token,
            "skill": skill_proper,
            "level": int(level)
        }
        
        # Try a direct skill setting approach
        result = self._make_request("POST", "/ai/setSkillLevel", data)
        
        if result.get("status") == "success":
            return f"Successfully set {skill_proper} to level {level}"
        else:
            # Fallback: use setCombatLevel if it's a combat skill
            combat_skills = ["accuracy", "strength", "defense", "health", "magic", "archery"]
            if skill.lower() in combat_skills:
                # For combat skills, we can only set all at once currently
                combat_result = self._make_request("POST", "/ai/setCombatLevel", {
                    "token": self.token,
                    "level": int(level)
                })
                
                if combat_result.get("status") == "success":
                    return f"Set all combat skills to level {level} (individual skill setting not available)"
                else:
                    return f"Failed to set skill level: {result.get('message', 'Unknown error')}"
            else:
                return f"Failed to set {skill_proper} level: {result.get('message', 'Individual non-combat skill setting not supported')}"

    def restore_hp_mp(self) -> str:
        """Restore HP and MP to maximum values"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        # First observe to get current max values
        try:
            observation_result = self.observe_environment({"radius": 1})
            if isinstance(observation_result, str) and "Environment observation" in observation_result:
                import re
                import json
                
                json_match = re.search(r'\{.*\}', observation_result, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    player_status = data.get("playerStatus", {})
                    
                    max_hp = player_status.get("maxHitPoints", 100)
                    max_mp = player_status.get("maxMana", 50)
                    
                    # Set HP and MP to max values
                    restore_data = {
                        "token": self.token,
                        "hitPoints": max_hp,
                        "mana": max_mp
                    }
                    
                    result = self._make_request("POST", "/ai/setPlayerStatus", restore_data)
                    
                    if result.get("status") == "success":
                        return f"Successfully restored HP to {max_hp} and MP to {max_mp}"
                    else:
                        return f"Failed to restore HP/MP: {result.get('message', 'Unknown error')}"
                else:
                    return "Error: Could not parse player status"
            else:
                return "Error: Could not get player status"
        except Exception as e:
            return f"Error restoring HP/MP: {str(e)}"

    def set_inventory(self, arguments: Dict[str, Any]) -> str:
        """Set inventory items (admin cheat command)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        items = arguments.get("items", [])
        clear_first = arguments.get("clearFirst", False)
        
        if not items:
            return "Error: Items list is required."
        
        data = {
            "token": self.token,
            "items": items,
            "clearFirst": clear_first
        }
        
        result = self._make_request("POST", "/ai/setInventory", data)
        
        if result.get("status") == "success":
            results = result.get("results", {})
            added_items = results.get("addedItems", [])
            failed_items = results.get("failedItems", [])
            
            success_count = len(added_items)
            total_count = len(items)
            
            message = f"Successfully added {success_count}/{total_count} items to inventory"
            
            if failed_items:
                failed_names = [item.get("key", "unknown") for item in failed_items]
                message += f". Failed items: {', '.join(failed_names)}"
            
            return message
        else:
            return f"Failed to set inventory: {result.get('message', 'Unknown error')}"

    def clear_equipment(self, arguments: Dict[str, Any] = None) -> str:
        """Clear all equipped items (admin cheat command)"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        data = {
            "token": self.token,
            "equipment": {},
            "clearFirst": True
        }
        
        result = self._make_request("POST", "/ai/setEquipments", data)
        
        if result.get("status") == "success":
            return "Successfully cleared all equipment"
        else:
            return f"Failed to clear equipment: {result.get('message', 'Unknown error')}"

    def chat(self, arguments: Dict[str, Any]) -> str:
        """Send a global group chat message to all agents/players in the game"""
        if not self.token:
            return "Error: No token available. Please login first."
        
        message = arguments.get("message", "")
        
        if not message:
            return "Error: Message content is required."
        
        # Always send as global message for group chat functionality
        data = {
            "token": self.token,
            "message": message,
            "global": True  # Force global for group chat
        }
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["chat"], data)
        
        if result.get("status") == "success":
            return f"Global chat message sent: {message}"
        else:
            return f"Failed to send global chat message: {result.get('message', 'Unknown error')}"

    def get_chat_messages(self) -> str:
        """Retrieve all chat messages from the current game session (for system prompt context)"""
        if not self.token:
            return "No chat messages available (not logged in)"
        
        try:
            # Use the global chat endpoint to get recent messages
            result = self._make_request(
                "GET", 
                AGENTWORLD_API_ENDPOINTS["get_chat"], 
                params={"token": self.token}
            )
            
            if result.get("status") == "success":
                messages = result.get("messages", [])
                if not messages:
                    return "No chat messages in current session"
                
                # Format messages for system prompt
                formatted_messages = []
                for msg in messages:
                    timestamp = msg.get("timestamp", "")
                    player = msg.get("player", "Unknown")
                    content = msg.get("message", "")
                    formatted_messages.append(f"[{timestamp}] {player}: {content}")
                
                return "\n".join(formatted_messages)
            else:
                return f"Failed to retrieve chat messages: {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            return f"Error retrieving chat messages: {str(e)}"

    def transfer_items(self, arguments: Dict[str, Any]) -> str:
        """Transfer items from current player's inventory to another player.
        
        This function implements a proper transfer mechanism:
        1. Verifies we have the required items in inventory
        2. Removes items from our inventory using setInventory API
        3. Adds items to target player's inventory using setInventory API with targetPlayer
        4. Provides proper rollback if the transfer fails
        5. Sends chat notification of the transfer
        """
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_player = arguments.get("targetPlayer", "")
        item_key = arguments.get("itemKey", "")
        count = arguments.get("count", 1)
        
        if not target_player:
            return "Error: Target player username is required."
        
        if not item_key:
            return "Error: Item key is required for transfer."
        
        try:
            count = int(count)
            if count < 1:
                return "Error: Count must be at least 1."
        except (ValueError, TypeError):
            return "Error: Count must be a valid integer."
        
        # Log the transfer attempt for debugging
        self._log_message(f"🔄 Transferring {count}x {item_key} to {target_player}", "debug")
        
        # First check if we have the item in inventory
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], 
                                          params={"token": self.token, "radius": 5})
        
        if observe_result.get("status") != "success":
            return f"Error: Could not check inventory: {observe_result.get('message', 'Unknown error')}"
        
        # Check current inventory for the item
        inventory = observe_result.get("inventory", {})
        items = inventory.get("items", [])
        
        # Find the item in inventory
        available_count = 0
        item_name = item_key
        for item in items:
            if item.get("key") == item_key:
                available_count += item.get("count", 0)
                item_name = item.get("name", item_key)
        
        if available_count < count:
            return f"Error: Not enough {item_name} in inventory. Have {available_count}, need {count}."
        
        # Get current inventory as a dictionary for easier manipulation
        current_inventory = {}
        for item in items:
            key = item.get("key")
            item_count = item.get("count", 0)
            if key:
                current_inventory[key] = current_inventory.get(key, 0) + item_count
        
        # Store original inventory for potential rollback BEFORE modifying it
        original_items = []
        for key, amount in current_inventory.items():
            if amount > 0:
                original_items.append({"key": key, "count": amount})
        
        # Remove items from current player's inventory
        current_inventory[item_key] = current_inventory.get(item_key, 0) - count
        if current_inventory[item_key] <= 0:
            del current_inventory[item_key]
        
        # Convert back to list format for setInventory API
        current_items = []
        for key, amount in current_inventory.items():
            if amount > 0:
                current_items.append({"key": key, "count": amount})
        
        # Update current player's inventory (remove transferred items)
        remove_data = {
            "token": self.token,
            "items": current_items,
            "clearFirst": True
        }
        
        remove_response = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["setInventory"], remove_data)
        
        if remove_response.get("status") != "success":
            return f"Error: Failed to remove items from inventory: {remove_response.get('message', 'Unknown error')}"
        
        # Add items to target player using setInventory with targetPlayer parameter
        target_items_list = [{"key": item_key, "count": count}]
        
        add_data = {
            "token": self.token,
            "targetPlayer": target_player,
            "items": target_items_list,
            "clearFirst": False  # Don't clear target player's inventory, just add items
        }
        
        self._log_message(f"🔄 Adding {count}x {item_key} to {target_player}'s inventory", "debug")
        add_response = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["setInventory"], add_data)
        
        transfer_success = False
        transfer_method = "setInventory_with_targetPlayer"
        
        if add_response.get("status") == "success":
            transfer_success = True
            results = add_response.get("results", {})
            added_items = results.get("addedItems", [])
            failed_items = results.get("failedItems", [])
            
            # Verify that the items were actually added
            if added_items and len(added_items) > 0:
                actual_added = sum(item.get("count", 0) for item in added_items if item.get("key") == item_key)
                if actual_added >= count:
                    self._log_message(f"✅ Transfer successful: {actual_added}x {item_key} added to {target_player}'s inventory", "debug")
                else:
                    transfer_success = False
                    self._log_message(f"❌ Partial transfer: only {actual_added}/{count}x {item_key} added", "warning")
            else:
                transfer_success = False
                self._log_message(f"❌ No items were added. Failed items: {failed_items}", "warning")
        else:
            error_msg = add_response.get("message", "Unknown error")
            self._log_message(f"❌ Transfer failed: {error_msg}", "debug")
            
            # Check for specific error messages to provide better feedback
            if "not found" in error_msg.lower():
                error_msg = f"Target player '{target_player}' is not online or does not exist"
            elif "invalid token" in error_msg.lower():
                error_msg = "Authentication failed - invalid token"
        
        if not transfer_success:
            # Transfer failed - rollback the inventory change
            self._log_message(f"❌ Transfer failed. Rolling back inventory changes.", "warning")
            
            # Rollback: restore original inventory
            rollback_data = {
                "token": self.token,
                "items": original_items,
                "clearFirst": True
            }
            rollback_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["setInventory"], rollback_data)
            
            if rollback_result.get("status") == "success":
                return f"Error: Transfer failed - {error_msg}. Inventory restored to original state."
            else:
                return f"Critical Error: Transfer failed AND inventory rollback failed. Items may be lost: {rollback_result.get('message', 'Unknown error')}"
        
        # Get current player username from observation
        player_status = observe_result.get("playerStatus", {})
        current_player = player_status.get("name") or player_status.get("username") or "Current Player"
        
        # Create success message
        success_message = f"✅ Transfer completed: {count}x {item_name} transferred from {current_player} to {target_player} (method: {transfer_method})"
        chat_message = f"Successfully transferred {count}x {item_name} to {target_player}"
        
        # Send chat message to notify the transfer
        chat_data = {
            "token": self.token,
            "message": chat_message,
            "global": True
        }
        
        chat_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["chat"], chat_data)
        
        self._log_message(f"📋 Transfer completed: {success_message}", "info")
        
        return success_message 