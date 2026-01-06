"""
Test script to verify attack_entity tool automatically picks up dropped items.

This script:
1. Logs in a test character
2. Boosts combat level
3. Observes the environment to find nearby mobs
4. Attacks a mob using attack_entity
5. Verifies that loot collection happened automatically
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


def test_attack_and_loot():
    # Initialize game tools with debug prints enabled
    game_tools = KaetramGameTools(debug_prints=True)

    # Login with a test character
    print("=" * 60)
    print("STEP 1: Logging in...")
    print("=" * 60)

    # Try different test agents in case one is already logged in
    test_agents = ["TestAgent6", "TestAgent7", "TestAgent8", "TestAgent9", "TestAgent10"]
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

    # Boost player combat level for testing
    print("\n" + "=" * 60)
    print("STEP 1.5: Boosting combat level for testing...")
    print("=" * 60)
    boost_result = game_tools.set_combat_level({"level": 99})
    print(f"Combat boost result: {boost_result}")

    # Also restore HP/MP
    restore_result = game_tools.restore_hp_mp()
    print(f"HP/MP restore result: {restore_result}")

    # Move to a remote location to avoid other agents
    print("\n" + "=" * 60)
    print("STEP 2: Moving to area with Rats...")
    print("=" * 60)

    # Move to forest area where Rats spawn (around 93, 95 based on earlier tests)
    move_result = game_tools._make_request(
        "POST",
        "/ai/move",
        {"token": game_tools.token, "x": 93, "y": 95}
    )
    print(f"Move result: {move_result}")
    time.sleep(2)

    # Observe environment to find mobs
    observe_result = game_tools._make_request(
        "GET",
        "/ai/observe",
        params={"token": game_tools.token, "radius": 64}
    )

    if observe_result.get("status") != "success":
        print(f"ERROR: Failed to observe: {observe_result}")
        return

    # Get player location
    location = observe_result.get("location", {})
    print(f"Player location: ({location.get('x')}, {location.get('y')})")

    # Get current inventory
    inventory = observe_result.get("inventory", {}).get("items", [])
    print(f"Current inventory ({len(inventory)} items):")

    # Check specifically for gold
    gold_before = 0
    for item in inventory:
        print(f"  - {item.get('name', 'Unknown')} x{item.get('count', 1)}")
        if item.get('key') == 'gold':
            gold_before += item.get('count', 0)

    print(f"\n*** GOLD BEFORE ATTACK: {gold_before} ***")

    # Find mobs
    mobs = observe_result.get("mobs", [])
    print(f"\nFound {len(mobs)} mobs nearby")

    if not mobs:
        print("No mobs found. Trying another location...")
        move_result = game_tools._make_request(
            "POST",
            "/ai/move",
            {"token": game_tools.token, "x": 100, "y": 100}
        )
        time.sleep(2)
        observe_result = game_tools._make_request(
            "GET",
            "/ai/observe",
            params={"token": game_tools.token, "radius": 64}
        )
        mobs = observe_result.get("mobs", [])
        location = observe_result.get("location", {})
        inventory = observe_result.get("inventory", {}).get("items", [])
        print(f"New location: ({location.get('x')}, {location.get('y')})")
        print(f"Found {len(mobs)} mobs")

    if not mobs:
        print("Still no mobs found. Exiting.")
        game_tools.logout_character()
        return

    # List first 5 mobs
    print("\nAvailable mobs:")
    for i, mob in enumerate(mobs[:5]):
        distance = abs(mob.get('x', 0) - location.get('x', 0)) + abs(mob.get('y', 0) - location.get('y', 0))
        print(f"  [{i}] {mob.get('name')} (Lvl {mob.get('level')}) at ({mob.get('x')}, {mob.get('y')}) - dist: {distance}")

    # Pick a Rat specifically (configured with 100% gold drop)
    rats = [m for m in mobs if m.get('name') == 'Rat']
    print(f"\nFound {len(rats)} Rats in the area")

    if not rats:
        print("No Rats found! Listing all mob types:")
        mob_types = {}
        for m in mobs:
            name = m.get('name', 'Unknown')
            mob_types[name] = mob_types.get(name, 0) + 1
        for name, count in sorted(mob_types.items()):
            print(f"  - {name}: {count}")
        print("\nPicking closest mob instead...")
        target_mob = min(mobs, key=lambda m: abs(m.get('x', 0) - location.get('x', 0)) + abs(m.get('y', 0) - location.get('y', 0)))
    else:
        # Pick a random Rat from the closest 5, excluding known stale instances
        import random
        stale_instances = ['3427461940']  # Known stale instance from previous tests
        valid_rats = [r for r in rats if r.get('instance') not in stale_instances]
        if not valid_rats:
            valid_rats = rats  # Fallback if all are stale

        closest_rats = sorted(valid_rats, key=lambda m: abs(m.get('x', 0) - location.get('x', 0)) + abs(m.get('y', 0) - location.get('y', 0)))[:5]
        target_mob = closest_rats[0]  # Pick the closest valid Rat
        print(f"Available Rats (closest 5, excluding stale):")
        for r in closest_rats:
            print(f"  - {r.get('name')} at ({r.get('x')}, {r.get('y')}) instance: {r.get('instance')}")

    print(f"\nSelected target: {target_mob.get('name')} (instance: {target_mob.get('instance')}) at ({target_mob.get('x')}, {target_mob.get('y')})")

    # Re-observe right before attack to ensure mob still exists
    print("\nRe-observing to verify target...")
    observe_fresh = game_tools._make_request(
        "GET",
        "/ai/observe",
        params={"token": game_tools.token, "radius": 64}
    )
    fresh_mobs = observe_fresh.get("mobs", [])
    target_still_exists = any(m.get("instance") == target_mob.get("instance") for m in fresh_mobs)
    print(f"Target still exists in fresh observation: {target_still_exists}")

    if not target_still_exists:
        print("Target mob no longer exists! Picking a new target from fresh observation...")
        if fresh_mobs:
            location = observe_fresh.get("location", {})
            target_mob = min(fresh_mobs, key=lambda m: abs(m.get('x', 0) - location.get('x', 0)) + abs(m.get('y', 0) - location.get('y', 0)))
            print(f"New target: {target_mob.get('name')} (instance: {target_mob.get('instance')})")
        else:
            print("No mobs available!")
            game_tools.logout_character()
            return

    print(f"\n" + "=" * 60)
    print(f"STEP 3: Attacking {target_mob.get('name')} (instance: {target_mob.get('instance')})")
    print("=" * 60)

    # Record inventory before attack
    inventory_before = {}
    for item in inventory:
        key = item.get("key", "")
        count = item.get("count", 0)
        if key:
            inventory_before[key] = inventory_before.get(key, 0) + count

    # Attack the mob - use attack_mob directly for more debug info
    print("\nCalling attack_entity...")
    attack_result = game_tools.attack_entity({
        "targetInstance": target_mob.get("instance")
    })

    print("\n" + "-" * 60)
    print("ATTACK RESULT:")
    print("-" * 60)
    print(attack_result)

    # Key observation: if player HP decreased, combat happened!
    print(f"\nHP change analysis: Started with boosted HP, check if damage was taken")

    # Check inventory after attack
    print("\n" + "=" * 60)
    print("STEP 4: Checking inventory and ground items after combat...")
    print("=" * 60)

    # Check with larger radius to find any ground items
    observe_after = game_tools._make_request(
        "GET",
        "/ai/observe",
        params={"token": game_tools.token, "radius": 32}
    )

    if observe_after.get("status") == "success":
        inventory_after_items = observe_after.get("inventory", {}).get("items", [])
        inventory_after = {}
        gold_after = 0

        print("Inventory after attack:")
        for item in inventory_after_items:
            key = item.get("key", "")
            count = item.get("count", 0)
            print(f"  - {item.get('name', 'Unknown')} x{count}")
            if key:
                inventory_after[key] = inventory_after.get(key, 0) + count
            if key == 'gold':
                gold_after += count

        print(f"\n*** GOLD AFTER ATTACK: {gold_after} ***")
        print(f"*** GOLD GAINED: {gold_after - gold_before} ***")

        # Compare inventories
        new_items = []
        for key, count in inventory_after.items():
            before_count = inventory_before.get(key, 0)
            if count > before_count:
                new_items.append(f"{key}: +{count - before_count}")

        if new_items:
            print("NEW ITEMS COLLECTED:")
            for item in new_items:
                print(f"  + {item}")
        else:
            print("No new items detected in inventory.")

        # Check ALL ground items in the area
        ground_items = observe_after.get("groundItems", [])
        print(f"\nGround items in area (radius 32): {len(ground_items)}")
        if ground_items:
            for gi in ground_items:
                print(f"  - {gi.get('name')} x{gi.get('count', 1)} at ({gi.get('x')}, {gi.get('y')}) instance: {gi.get('instance')}")
        else:
            print("  No ground items found in the area")

    # Logout
    print("\n" + "=" * 60)
    print("STEP 5: Logging out...")
    print("=" * 60)
    logout_result = game_tools.logout_character()
    print(f"Logout result: {logout_result}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_attack_and_loot()
