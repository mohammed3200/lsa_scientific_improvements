"""
Run the full NIST SP 800-22 statistical test suite on LSA ciphertext output.

Generates:
  - results/nist_test_results.json
  - results/nist_summary_table.md
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nist_suite import generate_lsa_bit_sequence, run_all_tests


def main() -> None:
    print("=" * 70)
    print("NIST SP 800-22 STATISTICAL TEST SUITE")
    print("=" * 70)
    print("Generating 1,000,000 bits of LSA ciphertext ...")
    bits = generate_lsa_bit_sequence(num_bits=1_000_000, seed=42)
    print("Running 15 statistical tests ...")
    print()

    results = run_all_tests(bits)

    # Console table
    print(f"{'#':<4} {'Test':<35} {'p-value':>12} {'Status':>8}")
    print("-" * 70)
    idx = 1
    for test_name, data in results.items():
        if "p_values" in data:
            print(f"{idx:<4} {test_name:<35} {'(multiple)':>12} {data['status']:>8}")
        else:
            p_str = f"{data['p_value']:.4f}" if data['p_value'] >= 0.0001 else f"{data['p_value']:.2e}"
            print(f"{idx:<4} {test_name:<35} {p_str:>12} {data['status']:>8}")
        idx += 1

    passed = sum(1 for d in results.values() if d['status'] == 'PASS')
    print()
    print(f"Summary: {passed}/{len(results)} tests PASSED (threshold p > 0.01)")
    print()

    # Save JSON
    os.makedirs("results", exist_ok=True)
    with open("results/nist_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[Save] results/nist_test_results.json")

    # Save Markdown table
    with open("results/nist_summary_table.md", "w") as f:
        f.write("# NIST SP 800-22 Test Results\n\n")
        f.write("| Test | p-value | Status |\n")
        f.write("|------|---------|--------|\n")
        for test_name, data in results.items():
            if "p_values" in data:
                p_str = "(see JSON)"
            else:
                p_str = f"{data['p_value']:.6f}" if data['p_value'] >= 0.000001 else f"{data['p_value']:.2e}"
            f.write(f"| {test_name} | {p_str} | {data['status']} |\n")
        f.write(f"\n**Overall:** {passed}/{len(results)} tests PASSED\n")
    print("[Save] results/nist_summary_table.md")


if __name__ == "__main__":
    main()
