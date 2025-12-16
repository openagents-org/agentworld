#!/usr/bin/env python3
"""
Human Study User Initialization Script
Initialize all player accounts based on task YAML file

Usage:
    python initialize_users.py --task ../data_v0.1_multi/benchmark/task_01_magic_staff.yaml

Features:
    1. Load task YAML configuration file
    2. Create account for each agent (default password: 123456)
    3. Set location, skills, items, equipment
    4. Logout so human players can login directly
"""

import argparse
import yaml
import requests
import json
import time
import sys
import os

# API Configuration
BASE_URL = "http://localhost:7031"
DEFAULT_PASSWORD = "123456"


def update_base_url(new_url: str):
    """Update API base URL"""
    global BASE_URL
    BASE_URL = new_url


def load_task_config(task_path: str) -> dict:
    """Load task YAML configuration"""
    with open(task_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_all_agents(config: dict) -> dict:
    """Get all agent configurations"""
    agents = {}
    for key, value in config.items():
        if key.startswith('agent_') and isinstance(value, dict):
            agents[key] = value
    return agents


def create_account(username: str, password: str) -> tuple:
    """Create account, returns (success, token, message)"""
    print(f"   🔑 Creating account {username}...")

    # Try to create account first
    try:
        resp = requests.post(f"{BASE_URL}/ai/create", json={
            "username": username,
            "password": password
        })
        data = resp.json()

        if data.get("status") == "success":
            print(f"   ✅ Account created successfully, logging in...")
            # Need to login after creation to get valid token
            time.sleep(0.3)
    except Exception as e:
        print(f"   ⚠️ Create request exception: {e}")

    # Login to get valid token
    try:
        resp = requests.post(f"{BASE_URL}/ai/login", json={
            "username": username,
            "password": password
        })
        data = resp.json()

        if data.get("status") == "success" and data.get("token"):
            print(f"   ✅ Login successful (token: {data['token'][:16]}...)")
            return True, data["token"], "logged_in"

        # May already be logged in, wait and retry
        if "already logged in" in data.get("message", "").lower():
            print(f"   ⚠️ Account already online, retrying after wait...")
            time.sleep(2)
            resp = requests.post(f"{BASE_URL}/ai/login", json={
                "username": username,
                "password": password
            })
            data = resp.json()
            if data.get("status") == "success" and data.get("token"):
                print(f"   ✅ Retry login successful (token: {data['token'][:16]}...)")
                return True, data["token"], "logged_in"

    except Exception as e:
        print(f"   ⚠️ Login request exception: {e}")

    print(f"   ❌ Account creation/login failed")
    return False, None, "failed"


def logout(token: str):
    """Logout"""
    try:
        resp = requests.post(f"{BASE_URL}/ai/logout", json={"token": token})
        if resp.status_code == 200 and resp.json().get("status") == "success":
            return True
    except:
        pass
    return False


def set_location(token: str, x: int, y: int) -> bool:
    """Set player location"""
    try:
        resp = requests.post(f"{BASE_URL}/ai/teleport", json={
            "token": token,
            "x": x,
            "y": y,
            "withAnimation": False
        })
        data = resp.json()
        if data.get("status") == "success":
            return True
        else:
            print(f"      [DEBUG] teleport failed: {data}")
            return False
    except Exception as e:
        print(f"      [DEBUG] teleport error: {e}")
        return False


def set_skill(token: str, skill: str, level: int) -> bool:
    """Set skill level"""
    # Skill name mapping
    skill_mapping = {
        "lumberjacking": "Lumberjacking",
        "accuracy": "Accuracy",
        "strength": "Strength",
        "defense": "Defense",
        "health": "Health",
        "magic": "Magic",
        "archery": "Archery",
        "mining": "Mining",
        "fishing": "Fishing",
        "cooking": "Cooking",
        "smithing": "Smithing",
        "crafting": "Crafting",
        "fletching": "Fletching",
        "foraging": "Foraging"
    }

    skill_name = skill_mapping.get(skill.lower(), skill)

    try:
        resp = requests.post(f"{BASE_URL}/ai/setSkillLevel", json={
            "token": token,
            "skill": skill_name,
            "level": level
        })
        data = resp.json()
        if data.get("status") == "success":
            return True
        else:
            print(f"      [DEBUG] setSkill {skill_name} failed: {data}")
            return False
    except Exception as e:
        print(f"      [DEBUG] setSkill error: {e}")
        return False


def set_inventory(token: str, items: list) -> bool:
    """Set inventory items"""
    # Convert format: [{"item": "flask", "count": 10}] -> [{"key": "flask", "count": 10}]
    formatted_items = []
    for item in items:
        formatted_items.append({
            "key": item.get("item"),
            "count": item.get("count", 1)
        })

    try:
        resp = requests.post(f"{BASE_URL}/ai/setInventory", json={
            "token": token,
            "items": formatted_items,
            "clearFirst": True
        })
        data = resp.json()
        if data.get("status") == "success":
            return True
        else:
            print(f"      [DEBUG] setInventory failed: {data}")
            return False
    except Exception as e:
        print(f"      [DEBUG] setInventory error: {e}")
        return False


def set_equipment(token: str, item_key: str, count: int = 1, enchant: int = 0) -> bool:
    """Set equipment"""
    # Determine equipment type based on item name
    item_lower = item_key.lower()
    if any(x in item_lower for x in ['sword', 'axe', 'bow', 'staff', 'dagger', 'mace', 'spear']):
        equipment_type = "weapon"
    elif any(x in item_lower for x in ['armor', 'armour', 'robe', 'tunic']):
        equipment_type = "armour"
    elif any(x in item_lower for x in ['boots', 'shoes', 'sandals']):
        equipment_type = "boots"
    elif any(x in item_lower for x in ['helmet', 'helm', 'hat', 'hood']):
        equipment_type = "helmet"
    elif any(x in item_lower for x in ['shield']):
        equipment_type = "shield"
    elif any(x in item_lower for x in ['pendant', 'necklace', 'amulet']):
        equipment_type = "pendant"
    elif any(x in item_lower for x in ['ring']):
        equipment_type = "ring"
    else:
        equipment_type = "weapon"

    enchantments = {}
    if enchant > 0:
        enchantments = {"damage": enchant, "accuracy": enchant, "defense": enchant}

    resp = requests.post(f"{BASE_URL}/ai/setEquipments", json={
        "token": token,
        "equipment": {
            equipment_type: {
                "key": item_key,
                "count": count,
                "enchantments": enchantments
            }
        },
        "clearFirst": False
    })

    return resp.status_code == 200 and resp.json().get("status") == "success"


def restore_hp_mp(token: str) -> bool:
    """Restore HP/MP"""
    resp = requests.post(f"{BASE_URL}/ai/setPlayerStatus", json={
        "token": token,
        "restoreToMax": True
    })
    return resp.status_code == 200 and resp.json().get("status") == "success"


def initialize_agent(agent_key: str, agent_config: dict, password: str) -> bool:
    """Initialize a single agent"""
    username = agent_config.get("username", agent_key)

    print(f"\n{'='*60}")
    print(f"🎮 Initializing {agent_key}: {username}")
    print(f"{'='*60}")

    # 1. Create/login account
    success, token, msg = create_account(username, password)
    if not success:
        print(f"   ❌ Cannot create/login account, skipping")
        return False

    time.sleep(0.3)

    results = []

    # 2. Set location
    location = agent_config.get("location", {})
    if location:
        x, y = location.get("x"), location.get("y")
        if x is not None and y is not None:
            if set_location(token, x, y):
                results.append(f"   ✅ Location: ({x}, {y})")
            else:
                results.append(f"   ⚠️ Location setting failed")
        time.sleep(0.2)

    # 3. Set skills
    skill_levels = agent_config.get("skill_levels", {})
    for skill, level in skill_levels.items():
        if set_skill(token, skill, level):
            results.append(f"   ✅ Skill {skill}: {level}")
        else:
            results.append(f"   ⚠️ Skill {skill} setting failed")
        time.sleep(0.1)

    # 4. Set inventory
    inventory_items = agent_config.get("inventory_items", [])
    if inventory_items:
        if set_inventory(token, inventory_items):
            items_str = ", ".join([f"{i['item']}x{i.get('count',1)}" for i in inventory_items])
            results.append(f"   ✅ Inventory: {items_str}")
        else:
            results.append(f"   ⚠️ Inventory setting failed")
        time.sleep(0.2)

    # 5. Set equipment
    equipped_items = agent_config.get("equipped_items", [])
    for item in equipped_items:
        item_key = item.get("item")
        count = item.get("count", 1)
        enchant = item.get("enchant", 0)
        if set_equipment(token, item_key, count, enchant):
            results.append(f"   ✅ Equipment: {item_key}")
        else:
            results.append(f"   ⚠️ Equipment {item_key} failed")
        time.sleep(0.1)

    # 6. Restore HP/MP
    if restore_hp_mp(token):
        results.append(f"   ✅ HP/MP restored")
    time.sleep(0.1)

    # 7. Logout
    if logout(token):
        results.append(f"   ✅ Logged out")
    else:
        results.append(f"   ⚠️ Logout failed")

    # Print results
    for r in results:
        print(r)

    print(f"\n   📋 Account info:")
    print(f"      Username: {username}")
    print(f"      Password: {password}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize all player accounts based on task YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python initialize_users.py --task ../data_v0.1_multi/benchmark/task_01_magic_staff.yaml
    python initialize_users.py --task ../data_v0.1_multi/benchmark/task_01_magic_staff.yaml --password mypass123
    python initialize_users.py --task ../data_v0.1_multi/benchmark/task_01_magic_staff.yaml --host http://192.168.1.100:7031
        """
    )

    parser.add_argument("--task", "-t", type=str, required=True,
                        help="Task YAML file path")
    parser.add_argument("--password", "-p", type=str, default=DEFAULT_PASSWORD,
                        help=f"Password for all accounts (default: {DEFAULT_PASSWORD})")
    parser.add_argument("--host", type=str, default=BASE_URL,
                        help=f"Game server address (default: {BASE_URL})")

    args = parser.parse_args()

    # Update server address
    update_base_url(args.host)

    # Check if file exists
    if not os.path.exists(args.task):
        print(f"❌ File not found: {args.task}")
        sys.exit(1)

    # Load configuration
    try:
        config = load_task_config(args.task)
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)

    # Get task info
    task_info = config.get("task", {})
    task_name = task_info.get("name", "Unknown Task")

    print("\n" + "=" * 70)
    print(f"🎯 HUMAN STUDY User Initialization")
    print("=" * 70)
    print(f"📋 Task: {task_name}")
    print(f"📁 File: {args.task}")
    print(f"🔑 Password: {args.password}")
    print(f"🌐 Server: {BASE_URL}")

    # Get all agents
    agents = get_all_agents(config)

    if not agents:
        print("❌ No agent configuration found")
        sys.exit(1)

    print(f"👥 Total {len(agents)} players to initialize")
    print("=" * 70)

    # Initialize each agent
    success_count = 0
    for agent_key in sorted(agents.keys()):
        agent_config = agents[agent_key]
        if initialize_agent(agent_key, agent_config, args.password):
            success_count += 1
        time.sleep(0.5)

    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Initialization complete: {success_count}/{len(agents)} accounts successful")
    print("=" * 70)

    print("\n📋 Account list:")
    for agent_key in sorted(agents.keys()):
        username = agents[agent_key].get("username", agent_key)
        print(f"   {agent_key}: {username} / {args.password}")

    print("\n💡 Human players can now login to these accounts in the browser!")
    print(f"   Game URL: http://localhost:7032/")


if __name__ == "__main__":
    main()
