"""
Generate side-channel resistance analysis report.

Outputs console report and saves Markdown to results/side_channel_report.md.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.side_channel import (
    timing_attack_resistance,
    dpa_resistance,
    fault_injection_resistance,
)


def main() -> None:
    print("=" * 70)
    print("SIDE-CHANNEL RESISTANCE ANALYSIS REPORT")
    print("=" * 70)
    print()

    key = 0xA5A5A5A5A5A5A5A5
    rkeys = __import__("lsa_project.algorithms.lsa.key_expansion", fromlist=["expand_key"]).expand_key(key)
    enc = lambda pt, k: __import__("lsa_project.algorithms.lsa.encrypt", fromlist=["lsa_encrypt"]).lsa_encrypt(pt, rkeys)

    timing = timing_attack_resistance(enc, key, samples=10_000)
    print(f"[1] Timing Attack Resistance")
    print(f"    Mean Time       : {timing['mean_ns']:.2f} ns")
    print(f"    Std Dev         : {timing['std_ns']:.2f} ns")
    print(f"    CV              : {timing['cv_percent']:.2f}%")
    print(f"    Threshold       : {timing['threshold_cv_percent']:.2f}%")
    print(f"    Status          : {timing['status']}")
    print()

    dpa = dpa_resistance(enc, key, samples=1_000)
    print(f"[2] DPA Resistance")
    print(f"    Max Correlation : {dpa['max_correlation']:.4f}")
    print(f"    Threshold       : {dpa['threshold']}")
    print(f"    Status          : {dpa['status']}")
    print()

    fault = fault_injection_resistance(enc, key, plaintext=0x123456789ABCDEF0, fault_rounds=100)
    print(f"[3] Fault Injection Resistance")
    print(f"    Detection Rate  : {fault['detection_rate_percent']:.1f}%")
    print(f"    Threshold       : {fault['threshold_percent']:.1f}%")
    print(f"    Status          : {fault['status']}")
    print()

    report = {"timing": timing, "dpa": dpa, "fault": fault}

    os.makedirs("results", exist_ok=True)
    with open("results/side_channel_report.md", "w") as f:
        f.write("# Side-Channel Resistance Report\n\n")
        f.write("| Test | Metric | Threshold | Result |\n")
        f.write("|------|--------|-----------|--------|\n")
        f.write(f"| Timing | CV | <{timing['threshold_cv_percent']}% | {timing['cv_percent']:.2f}% {timing['status']} |\n")
        f.write(f"| DPA | Max Corr | <{dpa['threshold']} | {dpa['max_correlation']:.4f} {dpa['status']} |\n")
        f.write(f"| Fault | Detection | {fault['threshold_percent']:.0f}% | {fault['detection_rate_percent']:.0f}% {fault['status']} |\n")
    print("[Save] results/side_channel_report.md")


if __name__ == "__main__":
    main()
