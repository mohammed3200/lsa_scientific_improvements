"""
Generate ASCON-128 comparison report.

Outputs console report and saves Markdown to results/ascon_comparison.md.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.ascon_comparison import ascon_comparison_table, security_margin_analysis


def main() -> None:
    print("=" * 70)
    print("NIST ASCON-128 STANDARD COMPARISON")
    print("=" * 70)
    print()

    table = ascon_comparison_table()
    headers = ["Feature", "ASCON-128", "LSA (Current)", "LSA (Recommended)"]
    print(f"{headers[0]:<25} {headers[1]:<20} {headers[2]:<25} {headers[3]:<25}")
    print("-" * 95)
    for row in table:
        print(f"{row['Feature']:<25} {row['ASCON-128']:<20} {row['LSA (Current)']:<25} {row['LSA (Recommended)']:<25}")
    print()

    margins = security_margin_analysis()
    print("[Security Margin Analysis — GPU Cluster @ 10^15 ops/sec]")
    print("-" * 70)
    for name, data in margins.items():
        label = name.replace("_", " ").title()
        print(f"  {label:<30} Key Space: 2^{int(math.log2(data['key_space']))}")
        print(f"    Breaking Time: {data['time_years']:.2e} years")
    print()

    os.makedirs("results", exist_ok=True)
    with open("results/ascon_comparison.md", "w") as f:
        f.write("# LSA vs NIST ASCON-128 Comparison\n\n")
        f.write("| Feature | ASCON-128 | LSA (Current) | LSA (Recommended) |\n")
        f.write("|---------|-----------|---------------|-------------------|\n")
        for row in table:
            f.write(f"| {row['Feature']} | {row['ASCON-128']} | {row['LSA (Current)']} | {row['LSA (Recommended)']} |\n")
        f.write("\n## Security Margin\n\n")
        for name, data in margins.items():
            label = name.replace("_", " ").title()
            f.write(f"- **{label}**: 2^{int(math.log2(data['key_space']))} keys, ~{data['time_years']:.2e} years to break\n")
    print("[Save] results/ascon_comparison.md")


if __name__ == "__main__":
    import math
    main()
