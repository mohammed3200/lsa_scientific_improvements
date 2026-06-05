"""
Generate theoretical security analysis report.

Outputs console report and saves JSON to results/security_theory_report.json.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.security_theory import generate_security_report


def format_time(seconds: float) -> str:
    if seconds > 1e12 * 365.25 * 86400:
        return f"{seconds / (1e12 * 365.25 * 86400):.2e} trillion years"
    elif seconds > 1e9 * 365.25 * 86400:
        return f"{seconds / (1e9 * 365.25 * 86400):.2e} billion years"
    elif seconds > 365.25 * 86400:
        return f"{seconds / (365.25 * 86400):.2e} years"
    elif seconds > 86400:
        return f"{seconds / 86400:.2f} days"
    else:
        return f"{seconds:.2f} seconds"


def main() -> None:
    report = generate_security_report()

    print("=" * 70)
    print("THEORETICAL SECURITY ANALYSIS REPORT")
    print("=" * 70)
    print()

    # Brute Force
    print("[1] Brute-Force Resistance")
    print("-" * 70)
    for label, data in [
        ("64-bit Key", report["brute_force_64bit"]),
        ("128-bit Key", report["brute_force_128bit"]),
    ]:
        print(f"  {label}:")
        print(f"    Key Space        : 2^{data['key_size_bits']} = {data['key_space']:,}")
        print(f"    Avg Trials       : {data['avg_trials']:.2e}")
        print(f"    Time (10^15 ops/s): {format_time(data['seconds'])}")
    print()

    # Differential
    print("[2] Differential Cryptanalysis Resistance")
    print("-" * 70)
    diff = report["differential_analysis"]
    print(f"  Rounds             : {diff['rounds']}")
    print(f"  S-Boxes per Round  : {diff['sboxes_per_round']}")
    print(f"  Total S-Boxes      : {diff['total_sboxes']}")
    print(f"  Min Active Needed  : {diff['min_active_for_security']}")
    print(f"  Expected Active    : {diff['expected_active_sboxes']}")
    print(f"  Security Margin    : {diff['security_margin']:.1f}x")
    print(f"  → With {diff['total_sboxes']} total S-boxes, differential trails")
    print(f"    require ≥{diff['expected_active_sboxes']} active S-boxes (threshold: 5).")
    print()

    # Linear
    print("[3] Linear Cryptanalysis Resistance")
    print("-" * 70)
    lin = report["linear_bias"]
    print(f"  Max LAT Bias       : {lin['sbox_lat_max']}")
    print(f"  Threshold          : {lin['threshold']}")
    print(f"  Status             : {lin['status']}")
    print()

    # Key Sensitivity
    print("[4] Key Sensitivity Test")
    print("-" * 70)
    ks = report["key_sensitivity"]
    print(f"  Hamming Distance   : {ks['hamming_distance']} / 64 bits")
    print(f"  Percentage         : {ks['percentage']:.2f}%")
    print(f"  Ideal              : {ks['ideal_distance']:.1f} bits (50.00%)")
    print(f"  Score              : {ks['score']:.2f}%")
    print()

    os.makedirs("results", exist_ok=True)
    with open("results/security_theory_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[Save] results/security_theory_report.json")


if __name__ == "__main__":
    main()
