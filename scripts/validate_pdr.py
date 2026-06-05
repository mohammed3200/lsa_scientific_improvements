"""
Validate Markov-based analytical PDR model against simulated baseline.

Generates comparison table and plot.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.pdr_model import fit_lambda_from_simulation, predict_pdr, validate_pdr_model


def main() -> None:
    # Baseline simulated PDR values (fractions)
    simulated = {
        "lsa":    {10: 0.955, 20: 0.945, 40: 0.936, 60: 0.925, 80: 0.912, 100: 0.896},
        "spn":    {10: 0.929, 20: 0.924, 40: 0.912, 60: 0.901, 80: 0.887, 100: 0.870},
        "feistel":{10: 0.900, 20: 0.895, 40: 0.885, 60: 0.874, 80: 0.864, 100: 0.842},
    }
    nodes = [10, 20, 40, 60, 80, 100]

    print("=" * 70)
    print("ANALYTICAL PDR MODEL VALIDATION")
    print("=" * 70)
    print()

    for algo in ["lsa", "spn", "feistel"]:
        lam = fit_lambda_from_simulation(simulated[algo], nodes)
        print(f"[{algo.upper()}] Fitted λ = {lam:.6f}")
        print(f"{'N':>6} {'Predicted':>12} {'Simulated':>12} {'Error %':>10}")
        print("-" * 45)
        for n in nodes:
            pred = predict_pdr(n, lam)
            sim = simulated[algo][n]
            err = abs(pred - sim) / sim * 100.0
            print(f"{n:>6} {pred:>12.4f} {sim:>12.4f} {err:>10.2f}")
        print()

    report = {"simulated": simulated, "nodes": nodes}
    os.makedirs("results", exist_ok=True)
    with open("results/pdr_validation.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[Save] results/pdr_validation.json")


if __name__ == "__main__":
    main()
