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
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or AGENTWORLD_BASE_URL
        self.token = None
        self.session = requests.Session()
        self.session.timeout = REQUEST_TIMEOUT
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Kaetram API with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["create"], data)
        
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
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["login"], data)
        
        if result.get("status") == "success":
            self.token = result.get("token")
            return f"Character {username} logged in successfully. Token obtained."
        else:
            return f"Failed to login: {result.get('message', 'Unknown error')}"

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
        
        data = {
            "token": self.token,
            "x": int(x),
            "y": int(y)
        }
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], data)
        
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
        
        # Find the resource in the environment data to determine its type
        resource_entity = None
        resource_type = None
        
        # Check in trees
        trees = observe_result.get("trees", [])
        for tree in trees:
            if tree.get("instance") == target_instance:
                resource_entity = tree
                resource_type = "tree"
                break
        
        # Check in rocks if not found in trees
        if not resource_entity:
            rocks = observe_result.get("rocks", [])
            for rock in rocks:
                if rock.get("instance") == target_instance:
                    resource_entity = rock
                    resource_type = "rock"
                    break
        
        # Check in fishing spots if not found in rocks
        if not resource_entity:
            fish_spots = observe_result.get("fishSpots", [])
            for fish_spot in fish_spots:
                if fish_spot.get("instance") == target_instance:
                    resource_entity = fish_spot
                    resource_type = "fishing spot"
                    break
        
        # Check in foraging spots if not found in fishing spots
        if not resource_entity:
            foraging = observe_result.get("foraging", [])
            for forage in foraging:
                if forage.get("instance") == target_instance:
                    resource_entity = forage
                    resource_type = "plant"
                    break
        
        if not resource_entity:
            return f"Error: Resource with instance {target_instance} not found in current environment."
        
        resource_name = resource_entity.get("name", "Unknown")
        resource_x = resource_entity.get("x")
        resource_y = resource_entity.get("y")
        
        # Get player current position
        location = observe_result.get("location", {})
        player_x = location.get("x")
        player_y = location.get("y")
        
        if player_x is None or player_y is None:
            return "Error: Could not determine player position."
        
        # Calculate distance to resource
        if resource_x is not None and resource_y is not None:
            distance = max(abs(resource_x - player_x), abs(resource_y - player_y))
            
            # Move closer if too far (resources typically need to be within 2 tiles)
            if distance > 2:
                move_data = {
                    "token": self.token,
                    "x": resource_x,
                    "y": resource_y
                }
                
                move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], move_data)
                
                if move_result.get("status") != "success":
                    return f"Error: Failed to move closer to {resource_name}: {move_result.get('message', 'Unknown error')}"
                
                # Wait briefly for position sync
                time.sleep(1)
                movement_info = f"Moved closer to {resource_name} at ({resource_x}, {resource_y}). "
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
        
        # Start the harvesting process
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["collect"], data)
        
        if result.get("status") != "success":
            return f"{movement_info}Failed to start {action} {resource_name}: {result.get('message', 'Unknown error')}"
        
        # CHEAT MODE: Force completion by repeatedly calling the API until resource is depleted
        max_attempts = 50  # Prevent infinite loops
        attempts = 0
        harvested_items = []
        
        while attempts < max_attempts:
            attempts += 1
            
            # Small delay to let server process
            time.sleep(0.1)
            
            # Check if resource is still there and try to harvest again
            current_observe = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 10})
            
            if current_observe.get("status") == "success":
                # Check if the target resource still exists
                resource_still_exists = False
                all_resources = []
                
                # Collect all resources from categorized arrays
                all_resources.extend(current_observe.get("trees", []))
                all_resources.extend(current_observe.get("rocks", []))
                all_resources.extend(current_observe.get("fishSpots", []))
                all_resources.extend(current_observe.get("foraging", []))
                
                for res in all_resources:
                    if res.get("instance") == target_instance:
                        resource_still_exists = True
                        break
                
                # If resource is gone, we're done!
                if not resource_still_exists:
                    break
                
                # Try harvesting again to speed up the process
                harvest_again = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["collect"], data)
                # Continue regardless of result - sometimes API returns error when already harvesting
            
            # Every 5 attempts, check inventory for new items
            if attempts % 5 == 0:
                current_inventory = {}
                if current_observe.get("status") == "success":
                    for item in current_observe.get("inventory", {}).get("items", []):
                        key = item.get("key", "")
                        count = item.get("count", 0)
                        if key:
                            current_inventory[key] = current_inventory.get(key, 0) + count
                
                # Check what items we gained
                for key, count in current_inventory.items():
                    initial_count = initial_inventory.get(key, 0)
                    if count > initial_count:
                        gained = count - initial_count
                        if key not in [item["key"] for item in harvested_items]:
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
            return result_message
            
        elif attempts >= max_attempts:
            return (
                f"{movement_info}⏳ HARVEST IN PROGRESS: {action.title()} {resource_name} at ({resource_x}, {resource_y})\n"
                f"📋 Status: Harvesting process started but may take additional time to complete\n"
                f"💡 Note: Check inventory periodically for collected items"
            )
        else:
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
        
        data = {
            "token": self.token,
            "type": skill,
            "itemKey": item_key,
            "count": count
        }
        
        result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["craft"], data)
        
        if result.get("status") == "success":
            item_info = result.get("item", {})
            return f"Successfully crafted {count}x {item_info.get('name', item_key)}!"
        else:
            # Handle missing materials error with detailed information
            missing_materials = result.get("missingMaterials", [])
            requirements = result.get("requirements", [])
            
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
            else:
                return f"Failed to craft {item_key}: {result.get('message', 'Unknown error')}"

    def attack_entity(self, arguments: Dict[str, Any]) -> str:
        """Attack an entity directly by providing its instance ID.
        
        This method will automatically:
        1. Find the target entity in the current environment
        2. Move to an adjacent position (up/down/left/right) if not already adjacent
        3. Wait briefly for position sync
        4. Initiate the attack
        5. After combat, move to the target's location to automatically pick up any dropped items
        
        Args:
            targetInstance: The instance ID of the entity to attack (from environment observation)
        """
        if not self.token:
            return "Error: No token available. Please login first."
        
        target_instance = arguments.get("targetInstance", "")
        
        if not target_instance:
            return "Error: Target instance is required for attack."
        
        # First, get current environment to find target location and player position
        observe_result = self._make_request("GET", AGENTWORLD_API_ENDPOINTS["observe"], params={"token": self.token, "radius": 64})
        
        if observe_result.get("status") != "success":
            return f"Error: Could not observe environment to locate target: {observe_result.get('message', 'Unknown error')}"
        
        # Extract player current position
        location = observe_result.get("location", {})
        player_x = location.get("x")
        player_y = location.get("y")
        
        if player_x is None or player_y is None:
            return "Error: Could not determine player position."
        
        # Find target entity in mobs list
        mobs = observe_result.get("mobs", [])
        target_entity = None
        
        for mob in mobs:
            if mob.get("instance") == target_instance:
                target_entity = mob
                break
        
        if not target_entity:
            return f"Error: Target entity {target_instance} not found in current environment."
        
        target_x = target_entity.get("x")
        target_y = target_entity.get("y")
        target_name = target_entity.get("name", "Unknown")
        
        if target_x is None or target_y is None:
            return f"Error: Could not determine target position for {target_name}."
        
        # Calculate distance to target (Manhattan distance for adjacent tiles)
        dx = abs(target_x - player_x)
        dy = abs(target_y - player_y)
        
        # Check if already adjacent (in one of the 4 cardinal directions)
        is_adjacent = (dx == 1 and dy == 0) or (dx == 0 and dy == 1)
        
        # If not adjacent, move to one of the 4 adjacent positions (up, down, left, right)
        if not is_adjacent:
            # Choose the best adjacent position based on current player position
            possible_positions = [
                (target_x, target_y - 1),  # Above target
                (target_x, target_y + 1),  # Below target
                (target_x - 1, target_y),  # Left of target
                (target_x + 1, target_y)   # Right of target
            ]
            
            # Find the closest adjacent position to current player position
            best_position = None
            min_distance = float('inf')
            
            for pos_x, pos_y in possible_positions:
                pos_distance = abs(pos_x - player_x) + abs(pos_y - player_y)
                if pos_distance < min_distance:
                    min_distance = pos_distance
                    best_position = (pos_x, pos_y)
            
            move_x, move_y = best_position
            
            # Move to attack position
            move_data = {
                "token": self.token,
                "x": move_x,
                "y": move_y
            }
            
            move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], move_data)
            
            if move_result.get("status") != "success":
                return f"Error: Failed to move to attack position: {move_result.get('message', 'Unknown error')}"
            
            # Wait briefly for position sync
            time.sleep(1)
            
            movement_info = f"Moved from ({player_x}, {player_y}) to ({move_x}, {move_y}) to attack {target_name}. "
        else:
            movement_info = f"Already adjacent to {target_name} at ({target_x}, {target_y}). "
        
        # Now initiate the attack
        attack_data = {
            "token": self.token,
            "targetInstance": target_instance
        }
        
        attack_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["attack"], attack_data)
        
        if attack_result.get("status") == "success":
            attack_info = f"{movement_info}Attack initiated successfully on {target_name}: {attack_result.get('message', 'Combat started')}"
            
            # Wait a moment for combat to potentially finish, then move to target location to pick up any drops
            time.sleep(3)  # Wait for combat to finish
            
            # Move to the exact target location to pick up any dropped items
            pickup_move_data = {
                "token": self.token,
                "x": target_x,
                "y": target_y
            }
            pickup_move_result = self._make_request("POST", AGENTWORLD_API_ENDPOINTS["move"], pickup_move_data)
            
            pickup_info = ""
            if pickup_move_result.get("status") == "success":
                pickup_info = f" After combat, moved to ({target_x}, {target_y}) to collect any dropped items."
            else:
                pickup_info = f" Combat finished, but failed to move to pickup location: {pickup_move_result.get('message', 'Unknown error')}"
            
            return f"{attack_info}{pickup_info}"
        else:
            return f"{movement_info}Failed to attack {target_name}: {attack_result.get('message', 'Unknown error')}"

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
        
        # Weapon patterns
        if any(weapon in item_key_lower for weapon in ['sword', 'bow', 'staff', 'dagger', 'axe', 'mace', 'spear']):
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
            
        except (ValueError, TypeError):
            return "Error: Invalid seconds value. Must be an integer between 1 and 60."

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
        
        # Use the existing setCombatLevel endpoint for individual skills by setting specific skill
        # For now, we'll use setPlayerStatus to try to modify levels
        data = {
            "token": self.token,
            "skill": skill_proper,
            "level": int(level)
        }
        
        # Try a direct skill setting approach (this may not exist in the API)
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