"""
Plot Packet Delivery Ratio (%) vs Number of Nodes.
"""

import matplotlib.pyplot as plt
from typing import Dict


def plot_pdr(
    lsa_data: Dict[int, float],
    spn_data: Dict[int, float],
    feistel_data: Dict[int, float],
    output_path: str = "results/plot_pdr.png",
):
    """Generate PDR plot."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = sorted(lsa_data.keys())
    y_lsa = [lsa_data[k] for k in x]
    y_spn = [spn_data[k] for k in x]
    y_feistel = [feistel_data[k] for k in x]

    ax.plot(x, y_lsa, marker="^", color="blue", label="LSA", linewidth=2, markersize=8)
    ax.plot(x, y_spn, marker="D", color="red", label="SPN", linewidth=2, markersize=7)
    ax.plot(x, y_feistel, marker="s", color="green", label="Feistel", linewidth=2, markersize=7)

    ax.set_xlabel("Number of Nodes", fontsize=12)
    ax.set_ylabel("Packet Delivery Ratio (%)", fontsize=12)
    ax.set_title("Packet Delivery Ratio vs Number of Nodes", fontsize=14, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(fontsize=11)
    ax.set_xticks(x)
    ax.set_ylim([70, 100])

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[Plot] Saved PDR plot to {output_path}")
