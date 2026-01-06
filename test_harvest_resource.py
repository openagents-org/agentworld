"""
Test script to verify harvest_resource tool automatically collects items into inventory.

This script:
1. Logs in a test character
2. Observes the environment to find nearby resources (trees, rocks, fish spots, foraging)
3. Records inventory before harvesting
4. Harvests a resource using harvest_resource
5. Verifies that items were automatically added to inventory (no ground pickup needed)
"""

import sys
import os
import json
import time

# Add agents directory to path so imports work correctly
sys.path.insert(0, '/home/ubuntu/works/agentworld/agents')
os.chdir('/home/ubuntu/works/agentworld/agents')

from game_tools import KaetramGameTools
from config import MASTER_PASSWORD


def test_harvest_resource():
    # Initialize game tools with debug prints enabled
    game_tools = KaetramGameTools(debug_prints=True)

    # Login with a test character
    print("=" * 60)
    print("STEP 1: Logging in...")
    print("=" * 60)

    # Try different test agents in case one is already logged in
    test_agents = ["TestAgent1", "TestAgent2", "TestAgent3", "TestAgent4", "TestAgent5"]
    logged_in = False

    for agent_name in test_agents:
        login_result = game_tools.login_character({
            "username": agent_name,
            "password": MASTER_PASSWORD
        })
        print(f"Login attempt for {agent_name}: {login_result}")

        if game_tools.token:
            logged_in = True
            print(f"Successfully logged in as {agent_name}")
            break

    if not logged_in:
        print("ERROR: Failed to login with any test agent. Exiting.")
        return

    # Boost skill levels for faster harvesting (DISABLED - testing 100% AI probability)
    # print("\n" + "=" * 60)
    # print("STEP 1.5: Boosting skill levels and equipping tools...")
    # print("=" * 60)

    # # Set high skill levels for all gathering skills
    # for skill in ["Lumberjacking", "Mining", "Fishing", "Foraging"]:
    #     skill_result = game_tools.set_individual_skill_level({"skill": skill, "level": 50})
    #     print(f"Set {skill} level: {skill_result}")

    # Give and equip an axe for tree cutting (still needed - tool requirement)
    print("\n" + "=" * 60)
    print("STEP 1.5: Equipping axe (no skill boost)...")
    print("=" * 60)
    equip_result = game_tools.give_and_equip_item({"itemKey": "axe", "slot": "Weapon"})
    print(f"Equip axe result: {equip_result}")

    # Restore HP/MP
    restore_result = game_tools.restore_hp_mp()
    print(f"HP/MP restore result: {restore_result}")

    # Observe environment to find resources
    print("\n" + "=" * 60)
    print("STEP 2: Observing environment for resources...")
    print("=" * 60)

    observe_result = game_tools._make_request(
        "GET",
        "/ai/observe",
        params={"token": game_tools.token, "radius": 64}
    )

    if observe_result.get("status") != "success":
        print(f"ERROR: Failed to observe: {observe_result}")
        game_tools.logout_character()
        return

    # Get player location
    location = observe_result.get("location", {})
    print(f"Player location: ({location.get('x')}, {location.get('y')})")

    # Get current inventory
    inventory = observe_result.get("inventory", {}).get("items", [])
    print(f"\nCurrent inventory ({len(inventory)} items):")
    for item in inventory:
        print(f"  - {item.get('name', 'Unknown')} x{item.get('count', 1)} (key: {item.get('key')})")

    # Find resources
    resources = observe_result.get("resources", [])
    print(f"\nFound {len(resources)} resources nearby")

    if not resources:
        print("No resources found. Trying to move to a forest area...")
        # Move to forest area where trees typically spawn
        move_result = game_tools._make_request(
            "POST",
            "/ai/move",
            {"token": game_tools.token, "x": 50, "y": 50}
        )
        print(f"Move result: {move_result}")
        time.sleep(3)

        observe_result = game_tools._make_request(
            "GET",
            "/ai/observe",
            params={"token": game_tools.token, "radius": 64}
        )
        resources = observe_result.get("resources", [])
        location = observe_result.get("location", {})
        inventory = observe_result.get("inventory", {}).get("items", [])
        print(f"New location: ({location.get('x')}, {location.get('y')})")
        print(f"Found {len(resources)} resources")

    if not resources:
        print("Still no resources found. Exiting.")
        game_tools.logout_character()
        return

    # Categorize resources by type
    trees = []
    rocks = []
    fish_spots = []
    foraging = []

    for resource in resources:
        name = resource.get("name", "").lower()
        if "tree" in name:
            trees.append(resource)
        elif "rock" in name:
            rocks.append(resource)
        elif "fish" in name:
            fish_spots.append(resource)
        else:
            foraging.append(resource)

    print(f"\nResource breakdown:")
    print(f"  - Trees: {len(trees)}")
    print(f"  - Rocks: {len(rocks)}")
    print(f"  - Fish spots: {len(fish_spots)}")
    print(f"  - Foraging: {len(foraging)}")

    # List first 5 resources of each type
    print("\nAvailable resources (closest first):")
    for resource_type, resource_list in [("Trees", trees), ("Rocks", rocks), ("Fish", fish_spots), ("Foraging", foraging)]:
        if resource_list:
            print(f"\n  {resource_type}:")
            sorted_resources = sorted(resource_list, key=lambda r: abs(r.get('x', 0) - location.get('x', 0)) + abs(r.get('y', 0) - location.get('y', 0)))
            for i, res in enumerate(sorted_resources[:3]):
                distance = abs(res.get('x', 0) - location.get('x', 0)) + abs(res.get('y', 0) - location.get('y', 0))
                print(f"    [{i}] {res.get('name')} at ({res.get('x')}, {res.get('y')}) - instance: {res.get('instance')} - dist: {distance}")

    # Pick a target resource (prefer trees since we have an axe equipped)
    target_resource = None
    if trees:
        sorted_trees = sorted(trees, key=lambda r: abs(r.get('x', 0) - location.get('x', 0)) + abs(r.get('y', 0) - location.get('y', 0)))
        target_resource = sorted_trees[0]
        resource_type = "tree"
    elif rocks:
        sorted_rocks = sorted(rocks, key=lambda r: abs(r.get('x', 0) - location.get('x', 0)) + abs(r.get('y', 0) - location.get('y', 0)))
        target_resource = sorted_rocks[0]
        resource_type = "rock"
    elif foraging:
        sorted_foraging = sorted(foraging, key=lambda r: abs(r.get('x', 0) - location.get('x', 0)) + abs(r.get('y', 0) - location.get('y', 0)))
        target_resource = sorted_foraging[0]
        resource_type = "foraging"
    elif fish_spots:
        sorted_fish = sorted(fish_spots, key=lambda r: abs(r.get('x', 0) - location.get('x', 0)) + abs(r.get('y', 0) - location.get('y', 0)))
        target_resource = sorted_fish[0]
        resource_type = "fish"

    if not target_resource:
        print("No suitable resource found to harvest. Exiting.")
        game_tools.logout_character()
        return

    print(f"\n" + "=" * 60)
    print(f"STEP 3: Selected target: {target_resource.get('name')}")
    print(f"        Instance: {target_resource.get('instance')}")
    print(f"        Location: ({target_resource.get('x')}, {target_resource.get('y')})")
    print(f"        Type: {resource_type}")
    print("=" * 60)

    # Pre-move closer to the resource to avoid position sync issues
    resource_x = target_resource.get('x')
    resource_y = target_resource.get('y')
    player_x = location.get('x')
    player_y = location.get('y')
    distance = abs(resource_x - player_x) + abs(resource_y - player_y)

    if distance > 2:
        print(f"\nPre-moving closer to resource (current distance: {distance})...")
        # Move to adjacent tile
        target_x = resource_x - 1 if resource_x > player_x else resource_x + 1
        target_y = resource_y - 1 if resource_y > player_y else resource_y + 1

        move_result = game_tools._make_request(
            "POST",
            "/ai/move",
            {"token": game_tools.token, "x": target_x, "y": target_y}
        )
        print(f"Move result: {move_result}")

        # Wait for movement to complete
        print("Waiting for movement to complete...")
        time.sleep(5)

        # Verify new position
        verify_observe = game_tools._make_request(
            "GET",
            "/ai/observe",
            params={"token": game_tools.token, "radius": 10}
        )
        if verify_observe.get("status") == "success":
            new_loc = verify_observe.get("location", {})
            new_distance = abs(resource_x - new_loc.get('x', 0)) + abs(resource_y - new_loc.get('y', 0))
            print(f"New position: ({new_loc.get('x')}, {new_loc.get('y')}), distance to resource: {new_distance}")
            inventory = verify_observe.get("inventory", {}).get("items", [])

    # Record inventory before harvest
    inventory_before = {}
    for item in inventory:
        key = item.get("key", "")
        count = item.get("count", 0)
        if key:
            inventory_before[key] = inventory_before.get(key, 0) + count

    print(f"\nInventory before harvest: {inventory_before}")

    # Check ground items before harvest
    ground_items_before = observe_result.get("groundItems", [])
    print(f"Ground items before harvest: {len(ground_items_before)}")

    print(f"\n" + "=" * 60)
    print(f"STEP 4: Harvesting {target_resource.get('name')}...")
    print("=" * 60)

    # Harvest the resource
    harvest_result = game_tools.harvest_resource({
        "targetInstance": target_resource.get("instance")
    })

    print("\n" + "-" * 60)
    print("HARVEST RESULT:")
    print("-" * 60)
    print(harvest_result)

    # Check inventory after harvest
    print("\n" + "=" * 60)
    print("STEP 5: Checking inventory and ground items after harvest...")
    print("=" * 60)

    # Wait longer for server-side processing if harvest is still in progress
    if "IN PROGRESS" in harvest_result:
        print("Harvest still in progress, waiting additional 30 seconds...")
        time.sleep(30)
    elif "COMPLETE" in harvest_result:
        print("Harvest completed!")
        time.sleep(1)
    else:
        time.sleep(1)

    observe_after = game_tools._make_request(
        "GET",
        "/ai/observe",
        params={"token": game_tools.token, "radius": 32}
    )

    if observe_after.get("status") == "success":
        inventory_after_items = observe_after.get("inventory", {}).get("items", [])
        inventory_after = {}

        print("\nInventory after harvest:")
        for item in inventory_after_items:
            key = item.get("key", "")
            count = item.get("count", 0)
            print(f"  - {item.get('name', 'Unknown')} x{count} (key: {key})")
            if key:
                inventory_after[key] = inventory_after.get(key, 0) + count

        # Compare inventories
        print("\n" + "-" * 60)
        print("INVENTORY COMPARISON:")
        print("-" * 60)

        new_items = []
        for key, count in inventory_after.items():
            before_count = inventory_before.get(key, 0)
            if count > before_count:
                new_items.append({"key": key, "gained": count - before_count})

        if new_items:
            print("*** NEW ITEMS COLLECTED (automatically added to inventory): ***")
            for item in new_items:
                print(f"  + {item['key']}: +{item['gained']}")
            print("\n*** SUCCESS: Items were automatically looted into inventory! ***")
        else:
            print("No new items detected in inventory.")
            print("(This could mean the resource didn't drop anything or there was an issue)")

        # Check ground items after harvest
        ground_items_after = observe_after.get("groundItems", [])
        print(f"\nGround items after harvest: {len(ground_items_after)}")

        if ground_items_after:
            print("Ground items found (these should NOT contain harvest loot):")
            for gi in ground_items_after:
                print(f"  - {gi.get('name')} x{gi.get('count', 1)} at ({gi.get('x')}, {gi.get('y')}) instance: {gi.get('instance')}")
        else:
            print("  No ground items found - good! (loot went directly to inventory)")

        # Verify the resource was depleted
        resources_after = observe_after.get("resources", [])
        resource_still_exists = any(r.get("instance") == target_resource.get("instance") for r in resources_after)
        print(f"\nTarget resource still exists: {resource_still_exists}")
        if not resource_still_exists:
            print("*** Resource was successfully depleted! ***")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    print(f"1. Target resource: {target_resource.get('name')} (instance: {target_resource.get('instance')})")
    print(f"2. Items gained: {new_items if new_items else 'None detected'}")
    print(f"3. Ground items after: {len(ground_items_after) if 'ground_items_after' in dir() else 'Unknown'}")
    print(f"4. Resource depleted: {'Yes' if not resource_still_exists else 'No'}")

    if new_items and not resource_still_exists:
        print("\n*** TEST PASSED: harvest_resource automatically collects items into inventory! ***")
    elif not resource_still_exists and not new_items:
        print("\n*** TEST INCONCLUSIVE: Resource depleted but no items detected (may not have dropped anything) ***")
    else:
        print("\n*** TEST NEEDS REVIEW: Check the results above ***")

    # Logout
    print("\n" + "=" * 60)
    print("STEP 6: Logging out...")
    print("=" * 60)
    logout_result = game_tools.logout_character()
    print(f"Logout result: {logout_result}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_harvest_resource()
