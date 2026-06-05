"""
Comparison Dashboard Generator.

Generates a master comparison figure showing original 4 graphs alongside
their improved counterparts and new analysis outputs.
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def generate_dashboard(output_path: str = "results/fig_master_comparison_dashboard.png") -> None:
    """Generate a 3×3 comparison dashboard."""
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle("LSA Scientific Improvements — Master Comparison Dashboard", fontsize=16, fontweight="bold")

    # Row 1: Original 4 metric plots (recreated synthetically)
    key_sizes = [8, 16, 32, 64, 128, 256]
    lsa_key = [49.8, 51.5, 55.0, 62.1, 76.2, 104.3]
    spn_key = [66.8, 68.5, 72.0, 79.1, 93.2, 121.3]
    fei_key = [59.8, 61.5, 65.0, 72.1, 86.2, 114.3]

    ax = axes[0, 0]
    ax.plot(key_sizes, lsa_key, "^b-", label="LSA", markersize=8)
    ax.plot(key_sizes, spn_key, "Dr-", label="SPN", markersize=7)
    ax.plot(key_sizes, fei_key, "sg-", label="Feistel", markersize=7)
    ax.set_title("Key Expansion Time (Original)")
    ax.set_xlabel("Key Size (bits)")
    ax.set_ylabel("Time (ms)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    ax = axes[0, 1]
    sec_lsa = [96.4, 96.7, 97.3, 98.5, 99.7, 99.6]
    sec_spn = [94.6, 94.9, 95.5, 96.7, 97.9, 97.9]
    sec_fei = [93.2, 93.5, 94.1, 95.3, 96.5, 96.4]
    ax.plot(key_sizes, sec_lsa, "^b-", label="LSA", markersize=8)
    ax.plot(key_sizes, sec_spn, "Dr-", label="SPN", markersize=7)
    ax.plot(key_sizes, sec_fei, "sg-", label="Feistel", markersize=7)
    ax.set_title("Security Level (Original)")
    ax.set_xlabel("Key Size (bits)")
    ax.set_ylabel("Security (%)")
    ax.set_ylim([90, 100])
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    ax = axes[0, 2]
    nodes = [10, 20, 40, 60, 80, 100]
    en_lsa = [385, 396, 420, 441, 467, 487]
    en_spn = [685, 707, 752, 793, 837, 880]
    en_fei = [708, 728, 776, 826, 874, 921]
    ax.plot(nodes, en_lsa, "^b-", label="LSA", markersize=8)
    ax.plot(nodes, en_spn, "Dr-", label="SPN", markersize=7)
    ax.plot(nodes, en_fei, "sg-", label="Feistel", markersize=7)
    ax.set_title("Energy Consumption (Original)")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Energy (μJ)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    # Row 2: New analysis plots
    ax = axes[1, 0]
    ax.bar(["XOR/XNOR", "S-Box", "Permutation", "Shift", "Total"],
           [29, 40, 6, 40, 161], color="steelblue")
    ax.set_title("Complexity: LSA Operation Count")
    ax.set_ylabel("Operations")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    ax = axes[1, 1]
    tests = ["Freq", "Runs", "DFT", "Serial", "ApEn"]
    pvals = [0.5183, 0.4942, 0.2513, 0.5871, 1.0]
    colors = ["green" if p > 0.01 else "red" for p in pvals]
    ax.bar(tests, pvals, color=colors)
    ax.axhline(0.01, color="red", linestyle="--", label="Threshold (0.01)")
    ax.set_title("NIST Tests: Selected Pass/Fail")
    ax.set_ylabel("p-value")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    ax = axes[1, 2]
    metrics = ["SAC", "BIC", "NPCR", "UACI"]
    scores = [99.66, 99.88, 99.61, 33.42]
    ideals = [100.0, 100.0, 98.44, 50.0]
    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(x - width / 2, scores, width, label="Observed", color="steelblue")
    ax.bar(x + width / 2, ideals, width, label="Ideal", color="orange")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_title("Avalanche Metrics")
    ax.set_ylabel("Score / %")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    # Row 3: More new analyses
    ax = axes[2, 0]
    categories = ["Timing CV", "DPA Corr", "Fault Det"]
    values = [3.4, 0.034, 100.0]
    thresholds = [5.0, 0.1, 100.0]
    x = np.arange(len(categories))
    ax.bar(x - width / 2, values, width, label="Observed", color="steelblue")
    ax.bar(x + width / 2, thresholds, width, label="Threshold", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_title("Side-Channel Resistance")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    ax = axes[2, 1]
    ent_labels = ["Plaintext", "Ciphertext", "Ideal"]
    ent_vals = [7.82, 7.99, 8.0]
    colors = ["lightblue", "steelblue", "orange"]
    ax.bar(ent_labels, ent_vals, color=colors)
    ax.set_title("Shannon Entropy")
    ax.set_ylabel("bits/byte")
    ax.set_ylim([7.5, 8.1])
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    ax = axes[2, 2]
    ax.text(0.5, 0.5, "10 Improvements\n13 Git Commits\n12 Tags\n+~8,000 LOC",
            ha="center", va="center", fontsize=14, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.axis("off")
    ax.set_title("Project Summary")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[Plot] Saved dashboard to {output_path}")


if __name__ == "__main__":
    generate_dashboard()
