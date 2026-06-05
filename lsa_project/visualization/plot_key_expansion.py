"""
Plot Key Expansion Time (ms) vs Key Size.
"""

import matplotlib.pyplot as plt
from typing import Dict


def plot_key_expansion(
    lsa_data: Dict[int, float],
    spn_data: Dict[int, float],
    feistel_data: Dict[int, float],
    output_path: str = "results/plot_key_expansion.png",
):
    """Generate Key Expansion Time plot."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = sorted(lsa_data.keys())
    y_lsa = [lsa_data[k] for k in x]
    y_spn = [spn_data[k] for k in x]
    y_feistel = [feistel_data[k] for k in x]

    ax.plot(x, y_lsa, marker="^", color="blue", label="LSA", linewidth=2, markersize=8)
    ax.plot(x, y_spn, marker="D", color="red", label="SPN", linewidth=2, markersize=7)
    ax.plot(x, y_feistel, marker="s", color="green", label="Feistel", linewidth=2, markersize=7)

    ax.set_xlabel("Key Size (bits)", fontsize=12)
    ax.set_ylabel("Key Expansion Time (ms)", fontsize=12)
    ax.set_title("Key Expansion Time vs Key Size", fontsize=14, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(fontsize=11)
    ax.set_xticks(x)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[Plot] Saved key expansion plot to {output_path}")
