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

    def logout_character(self) -> str:
        """Logout the current character and invalidate token"""
        if not self.token:
            return "No active session to logout"
        
        data = {"token": self.token}
        result = self._make_request("POST", KAETRAM_API_ENDPOINTS["logout"], data)
        
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