"""
Generate key space and entropy analysis report.

Outputs console report and saves JSON to results/entropy_report.json.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.entropy_analysis import generate_entropy_report


def main() -> None:
    print("=" * 70)
    print("KEY SPACE & ENTROPY ANALYSIS REPORT")
    print("=" * 70)
    print()

    report = generate_entropy_report()

    ks = report["key_space"]
    print(f"[1] Key Space Collision Test")
    print(f"    Keys Tested     : {ks['keys_tested']:,}")
    print(f"    Collisions      : {ks['collisions']}")
    print(f"    Effective Space : {ks['effective_key_space_percent']:.2f}%")
    print()

    print(f"[2] Shannon Entropy")
    print(f"    Plaintext       : {report['plaintext_entropy_bits_per_byte']:.2f} bits/byte")
    print(f"    Ciphertext      : {report['ciphertext_entropy_bits_per_byte']:.2f} bits/byte")
    print(f"    Ideal (random)  : 8.00 bits/byte")
    print()

    chi = report["chi_square"]
    print(f"[3] Chi-Square Test on Ciphertext")
    print(f"    χ² Statistic    : {chi['chi_square']:.2f}")
    print(f"    Degrees of Freedom: {chi['degrees_of_freedom']}")
    print(f"    p-value         : {chi['p_value']:.4f}")
    print(f"    Status          : {chi['status']}")
    print()

    os.makedirs("results", exist_ok=True)
    with open("results/entropy_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[Save] results/entropy_report.json")


if __name__ == "__main__":
    main()
