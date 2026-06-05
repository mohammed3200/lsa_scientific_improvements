"""
Generate complexity comparison table for LSA vs SPN vs Feistel.

Outputs console table and saves JSON to results/complexity_report.json.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lsa_project"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.complexity import compare_complexity


def main() -> None:
    algorithms = ["lsa", "spn", "feistel"]
    results = {}

    print("=" * 70)
    print("COMPUTATIONAL COMPLEXITY COMPARISON")
    print("=" * 70)
    print()

    # Header
    header = f"{'Operation':<20} {'LSA':>10} {'SPN':>10} {'Feistel':>10}"
    print(header)
    print("-" * 70)

    for algo in algorithms:
        results[algo] = compare_complexity(algo)

    # Extract summary rows
    ops = ["xor_xnor", "s_box", "permutation", "shift", "total"]
    op_labels = {
        "xor_xnor": "XOR / XNOR",
        "s_box": "S-Box lookups",
        "permutation": "Permutation",
        "shift": "Left Shift",
        "total": "Total",
    }

    for op in ops:
        row = f"{op_labels[op]:<20}"
        for algo in algorithms:
            val = results[algo]["summary"][op]
            row += f" {val:>10}"
        print(row)

    print()
    print("Asymptotic Complexity:")
    for algo in algorithms:
        asym = results[algo]["encryption"]["asymptotic"]
        print(f"  {algo.upper():<10} {asym}")
    print()

    os.makedirs("results", exist_ok=True)
    with open("results/complexity_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[Save] results/complexity_report.json")


if __name__ == "__main__":
    main()
