"""
Generate quantitative avalanche analysis report.

Outputs console report and saves JSON to results/avalanche_report.json.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.avalanche import (
    strict_avalanche_criterion,
    bit_independence_criterion,
    npcr_test,
    uaci_test,
)


def main() -> None:
    random = __import__("random")
    random.seed(42)

    plaintext = 0x123456789ABCDEF0
    key = 0xA5A5A5A5A5A5A5A5
    plaintext2 = plaintext ^ (1 << random.randint(0, 63))

    print("=" * 70)
    print("QUANTITATIVE AVALANCHE ANALYSIS REPORT")
    print("=" * 70)
    print()

    sac = strict_avalanche_criterion(plaintext, key, samples=10_000)
    print(f"[1] Strict Avalanche Criterion (SAC)")
    print(f"    Samples         : {sac['samples']:,}")
    print(f"    Avg Hamming     : {sac['avg_hamming_distance']:.2f} / {sac['ideal_distance']:.2f} bits")
    print(f"    Std Dev         : {sac['std_dev']:.4f}")
    print(f"    SAC Score       : {sac['sac_score_percent']:.2f}%")
    print()

    bic = bit_independence_criterion(plaintext, key, samples=5_000)
    print(f"[2] Bit Independence Criterion (BIC)")
    print(f"    Samples         : {bic['samples']:,}")
    print(f"    Max Correlation : {bic['max_correlation']:.4f}")
    print(f"    Avg Correlation : {bic['avg_correlation']:.4f}")
    print(f"    BIC Score       : {bic['bic_score_percent']:.2f}%")
    print()

    npcr = npcr_test(plaintext, plaintext2, key)
    print(f"[3] NPCR (Number of Pixels Change Rate)")
    print(f"    Changed Bits    : {npcr['changed_bits']} / {npcr['total_bits']}")
    print(f"    NPCR            : {npcr['npcr_percent']:.2f}%")
    print(f"    Ideal           : {npcr['ideal_percent']:.2f}%")
    print()

    uaci = uaci_test(plaintext, plaintext2, key)
    print(f"[4] UACI (Unified Average Changing Intensity)")
    print(f"    Changed Bits    : {uaci['changed_bits']} / {uaci['total_bits']}")
    print(f"    UACI            : {uaci['uaci_percent']:.2f}%")
    print(f"    Ideal           : {uaci['ideal_percent']:.2f}%")
    print()

    report = {
        "sac": sac,
        "bic": bic,
        "npcr": npcr,
        "uaci": uaci,
    }

    os.makedirs("results", exist_ok=True)
    with open("results/avalanche_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[Save] results/avalanche_report.json")


if __name__ == "__main__":
    main()
