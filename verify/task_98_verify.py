"""
Task 98: Mining Conglomerate Verification

Primary Objective: Establish mining conglomerate operating 4 mine sites, producing
100+ bars and 20+ finished products within 55 rounds

Success Criteria (from YAML):
- Total 120+ ores extracted (ironore + goldore + coal)
- Total 100+ bars smelted (ironbar + goldbar + other bars)
- Total 20+ finished products crafted (heavysword, axe, goldring, etc.)
"""
import argparse
import json


def task_98_verifier(traj_json):
    """
    Verify Task 98: Mining Conglomerate
    Check total ores, bars, and finished products across all agents
    """
    # Get final inventory for each agent
    inventory = {}
    for r in traj_json['rounds']:
        for act in r['actions']:
            if 'observation' in act and 'inventory' in act['observation']:
                inventory[act['agent_name']] = act['observation']['inventory']['items']

    # Define item categories
    ore_keys = ["ironore", "goldore", "coal"]
    bar_keys = ["ironbar", "goldbar", "bronzebar", "silverbar", "steelbar"]
    product_keys = ["heavysword", "axe", "goldring", "silverring", "pickaxe", "sword", "dagger"]

    # Count totals across all agents
    ore_totals = {}
    bar_totals = {}
    product_totals = {}

    for items in inventory.values():
        for item in items:
            k = item.get("key", "").lower()
            x = item.get("count", 0)

            if k in ore_keys:
                ore_totals[k] = ore_totals.get(k, 0) + x
            elif k in bar_keys:
                bar_totals[k] = bar_totals.get(k, 0) + x
            elif k in product_keys:
                product_totals[k] = product_totals.get(k, 0) + x

    total_ores = sum(ore_totals.values())
    total_bars = sum(bar_totals.values())
    total_products = sum(product_totals.values())

    print(f'Ore breakdown: {ore_totals}')
    print(f'Total ores: {total_ores}')
    print()
    print(f'Bar breakdown: {bar_totals}')
    print(f'Total bars: {total_bars}')
    print()
    print(f'Product breakdown: {product_totals}')
    print(f'Total products: {total_products}')

    ore_passed = total_ores >= 120
    bar_passed = total_bars >= 100
    product_passed = total_products >= 20
    passed = ore_passed and bar_passed and product_passed

    print(f'\nChecks:')
    print(f'  total ores >= 120: {"PASSED" if ore_passed else "FAILED"} ({total_ores}/120)')
    print(f'  total bars >= 100: {"PASSED" if bar_passed else "FAILED"} ({total_bars}/100)')
    print(f'  total products >= 20: {"PASSED" if product_passed else "FAILED"} ({total_products}/20)')
    print(f'\nResult: {"PASSED" if passed else "FAILED"}')

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify Task 98: Mining Conglomerate")
    parser.add_argument("--traj_path", type=str, required=True, help="Path to trajectory JSON file")
    args = parser.parse_args()

    with open(args.traj_path, 'r') as fin:
        traj_json = json.load(fin)
        passed = task_98_verifier(traj_json)
        exit(0 if passed else 1)


if __name__ == "__main__":
    main()
