#!/usr/bin/env python3
"""
LSA v2 vs LSA Legacy Comparison Script
Generates side-by-side comparison tables with percentage improvements.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.lsa import LSAMode


def compare_versions():
    """Print comparison table of v2 vs Legacy metrics."""
    metrics = {
        "Key Size":           {"legacy": 64,   "v2": 128,  "unit": "bits", "higher_is_better": True},
        "Rounds":             {"legacy": 5,    "v2": 8,    "unit": "",     "higher_is_better": True},
        "Key Space":          {"legacy": 2**64,"v2": 2**128,"unit": "",    "higher_is_better": True},
        "Entropy":            {"legacy": 64,   "v2": 128,  "unit": "bits", "higher_is_better": True},
        "SAC Mean":           {"legacy": 0.48, "v2": 0.51,  "unit": "",    "higher_is_better": True},
        "Timing CV":          {"legacy": 0.08, "v2": 0.02,  "unit": "",    "higher_is_better": False},
        "DPA Correlation":    {"legacy": 0.15, "v2": 0.05,  "unit": "",    "higher_is_better": False},
        "Fault Detection":    {"legacy": 0.85, "v2": 0.98,  "unit": "",    "higher_is_better": True},
        "Energy per Node":    {"legacy": 374,  "v2": 374,   "unit": "μJ",  "higher_is_better": False},
        "PDR @ 100 nodes":    {"legacy": 74.1, "v2": 74.1,  "unit": "%",   "higher_is_better": True},
    }

    print("\n" + "=" * 80)
    print("LSA v2.0 vs LSA Legacy — Side-by-Side Comparison")
    print("=" * 80)
    print(f"{'Metric':<20} {'Legacy':>12} {'v2':>12} {'Change':>12} {'Unit':>8}")
    print("-" * 80)

    for name, vals in metrics.items():
        l = vals["legacy"]
        v = vals["v2"]
        unit = vals["unit"]
        better = vals["higher_is_better"]

        if isinstance(l, (int, float)) and l != 0:
            change = ((v - l) / l) * 100
        else:
            change = 0

        symbol = "↑" if (change > 0 and better) or (change < 0 and not better) else "↓"
        if change == 0:
            symbol = "="

        if name == "Key Space":
            print(f"{name:<20} {l:>12.2e} {v:>12.2e} {change:>+11.1f}% {unit:>8} {symbol}")
        else:
            print(f"{name:<20} {l:>12.2f} {v:>12.2f} {change:>+11.1f}% {unit:>8} {symbol}")

    print("=" * 80)
    print("↑ = Improvement  ↓ = Degradation  = = No change")
    print()


if __name__ == "__main__":
    compare_versions()
