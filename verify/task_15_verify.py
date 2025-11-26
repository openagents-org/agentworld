"""
Task 15: Jellyfish Smoothie Verification

Primary Objective: Create a jellyfish smoothie through coordinated exotic fishing
and specialty beverage preparation

Success: Any agent has jellyfishsmoothie in inventory
"""
import argparse
import json


def task_15_verifier(traj_json):
    """
    Verify Task 15: Jellyfish Smoothie
    Check if any agent has crafted jellyfishsmoothie
    """
    inventory = {}

    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    cnt = {
        "jellyfishsmoothie": 0,
        "jellyfish": 0,
        "bowlsmall": 0
    }

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in cnt:
                cnt[k] += x

    jellyfishsmoothie = cnt["jellyfishsmoothie"]
    jellyfish = cnt["jellyfish"]
    bowlsmall = cnt["bowlsmall"]

    print(f'jellyfishsmoothie: {jellyfishsmoothie}')
    print(f'jellyfish (intermediate): {jellyfish}')
    print(f'bowlsmall (intermediate): {bowlsmall}')

    passed = jellyfishsmoothie >= 1
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')
    print(f'Required: jellyfishsmoothie >= 1, Actual: {jellyfishsmoothie}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 15: Jellyfish Smoothie")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_15_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
