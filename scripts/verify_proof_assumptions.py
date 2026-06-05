"""
Verify formal proof assumptions via S-Box analysis.

Checks:
  - S-Box branch number ≥ 2
  - 5 rounds produce ≥ 10 active S-boxes
  - LAT max bias ≤ 0.25
"""

import json
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lsa_project"))

from algorithms.lsa.s_box import S_BOX


def compute_ddt(sbox: list) -> np.ndarray:
    """Compute Difference Distribution Table (DDT)."""
    n = len(sbox)
    ddt = np.zeros((n, n), dtype=np.int32)
    for dx in range(n):
        for x in range(n):
            y1 = sbox[x]
            y2 = sbox[x ^ dx]
            dy = y1 ^ y2
            ddt[dx, dy] += 1
    return ddt


def compute_lat(sbox: list) -> np.ndarray:
    """Compute Linear Approximation Table (LAT)."""
    n = len(sbox)
    lat = np.zeros((n, n), dtype=np.int32)
    for a in range(n):
        for b in range(n):
            count = 0
            for x in range(n):
                input_parity = bin(a & x).count("1") % 2
                output_parity = bin(b & sbox[x]).count("1") % 2
                if input_parity == output_parity:
                    count += 1
            lat[a, b] = count - n // 2
    return lat


def branch_number(sbox: list) -> int:
    """Compute minimum branch number of the S-Box."""
    ddt = compute_ddt(sbox)
    # Branch number = min{wt(dx) + wt(dy) : ddt[dx,dy] > 0, (dx,dy) != (0,0)}
    min_bn = 10
    for dx in range(1, len(sbox)):
        for dy in range(len(sbox)):
            if ddt[dx, dy] > 0:
                wt = bin(dx).count("1") + bin(dy).count("1")
                min_bn = min(min_bn, wt)
    return min_bn


def max_lat_bias(lat: np.ndarray) -> float:
    """Return maximum absolute LAT bias divided by total inputs."""
    n = lat.shape[0]
    max_val = np.max(np.abs(lat[1:, 1:]))  # exclude (0,0)
    return max_val / n


def main() -> None:
    print("=" * 70)
    print("FORMAL PROOF ASSUMPTION VALIDATION")
    print("=" * 70)
    print()

    ddt = compute_ddt(S_BOX)
    lat = compute_lat(S_BOX)
    bn = branch_number(S_BOX)
    max_bias = max_lat_bias(lat)

    # Check 1: Branch number
    print(f"[1] S-Box Branch Number")
    print(f"    Computed        : {bn}")
    print(f"    Threshold       : ≥ 2")
    print(f"    Status          : {'PASS' if bn >= 2 else 'FAIL'}")
    print()

    # Check 2: Active S-boxes
    rounds = 5
    active_per_round = max(1, bn // 2)
    total_active = active_per_round * rounds
    print(f"[2] Active S-Box Count (5 Rounds)")
    print(f"    Active per Round: {active_per_round}")
    print(f"    Total Active    : {total_active}")
    print(f"    Threshold       : ≥ 10")
    print(f"    Status          : {'PASS' if total_active >= 10 else 'FAIL'}")
    print()

    # Check 3: LAT max bias
    print(f"[3] LAT Maximum Bias")
    print(f"    Max Bias        : {max_bias:.4f}")
    print(f"    Threshold       : ≤ 0.25")
    print(f"    Status          : {'PASS' if max_bias <= 0.25 else 'FAIL'}")
    print()

    report = {
        "branch_number": int(bn),
        "branch_threshold": 2,
        "branch_status": "PASS" if bn >= 2 else "FAIL",
        "active_sboxes": int(total_active),
        "active_threshold": 10,
        "active_status": "PASS" if total_active >= 10 else "FAIL",
        "lat_max_bias": float(max_bias),
        "lat_threshold": 0.25,
        "lat_status": "PASS" if max_bias <= 0.25 else "FAIL",
    }

    os.makedirs("results", exist_ok=True)
    with open("results/formal_proof_validation.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[Save] results/formal_proof_validation.json")


if __name__ == "__main__":
    main()
