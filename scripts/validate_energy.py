"""
Validate analytical energy model against simulated baseline values.

Generates comparison table and plot.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.energy_model import total_network_energy, validate_model


def main() -> None:
    # Baseline simulated averages from original paper
    simulated = {
        "lsa": {10: 385.3, 20: 396.5, 40: 420.1, 60: 440.7, 80: 466.9, 100: 487.5},
        "spn": {10: 684.7, 20: 707.4, 40: 751.7, 60: 793.3, 80: 837.3, 100: 879.6},
        "feistel": {10: 707.6, 20: 728.1, 40: 776.4, 60: 825.6, 80: 874.5, 100: 920.6},
    }

    overheads = {"lsa": 1.0, "spn": 2.0, "feistel": 2.1}

    print("=" * 70)
    print("ANALYTICAL ENERGY MODEL VALIDATION")
    print("=" * 70)
    print()

    for algo in ["lsa", "spn", "feistel"]:
        print(f"[{algo.upper()}]")
        print(f"{'Nodes':>8} {'Analytical':>14} {'Simulated':>14} {'Error %':>10}")
        print("-" * 50)

        analytical = {}
        for n in [10, 20, 40, 60, 80, 100]:
            res = total_network_energy(
                n_nodes=n,
                packets_per_node=50,
                packet_bits=512,
                avg_distance_m=30.0,
                algorithm_overhead=overheads[algo],
            )
            analytical[n] = res["total_energy_uj"]

        errors = validate_model(simulated[algo], analytical)
        for n in [10, 20, 40, 60, 80, 100]:
            print(f"{n:>8} {analytical[n]:>14.2f} {simulated[algo][n]:>14.2f} {errors[n]:>10.2f}")
        print()

    # Save JSON
    report = {
        "simulated": simulated,
        "overheads": overheads,
    }
    os.makedirs("results", exist_ok=True)
    with open("results/energy_validation.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[Save] results/energy_validation.json")


if __name__ == "__main__":
    main()
