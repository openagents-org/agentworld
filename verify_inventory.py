import argparse
import json


def task_02_verifier(traj_json):
    inventory = {}
    
    for r in traj_json['rounds']:
        for act in r['actions']:
            inventory[act['agent_name']] = act['observation']['inventory']['items']

    cnt = {
        "arrow": 0,
        "feather": 0,
        "stick": 0,
        "logs": 0
    }
    
    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)
            if k in cnt:
                cnt[k] += x

    arrows, feathers, sticks, logs = cnt["arrow"], cnt["feather"], cnt["stick"], cnt["logs"]
    total_sticks_available = sticks + (logs * 4)
    potential_arrows = min(feathers, total_sticks_available)

    score = (arrows * 10) + (potential_arrows * 5)
    score = max(score, 100)

    print(f'Feathers: {feathers}, Sticks: {sticks}, Logs: {logs}')
    print(f'Score: {score} / 100')
    
    return score

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traj_path", type=str)
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        task_02_verifier(traj_json)
    

if __name__ == "__main__":
    main()
