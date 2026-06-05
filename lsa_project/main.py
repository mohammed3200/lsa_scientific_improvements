"""
Main simulation runner for LSA Research Reproduction.

Reproduces four evaluation graphs and benchmark tables from:
Mahlake et al., Journal of Communications, Vol. 18, No. 1, 2023.
"""

import os
import sys
import json
import csv

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms.lsa.key_expansion import expand_key
from algorithms.lsa.encrypt import lsa_encrypt, lsa_decrypt

from metrics.key_expansion_time import measure_key_expansion_time
from metrics.security_meter import measure_security_level
from metrics.energy_consumption import measure_energy_consumption
from metrics.pdr_calculator import measure_pdr

from visualization.plot_key_expansion import plot_key_expansion
from visualization.plot_security import plot_security
from visualization.plot_energy import plot_energy
from visualization.plot_pdr import plot_pdr

from config import CipherParams


def sanity_check_cipher():
    """Quick encrypt/decrypt round-trip test."""
    print("=" * 60)
    print("SANITY CHECK: LSA Encrypt / Decrypt Round-Trip")
    print("=" * 60)

    key = 0xA5A5A5A5A5A5A5A5
    plaintext = 0x123456789ABCDEF0

    round_keys = expand_key(key)
    print(f"Plaintext : 0x{plaintext:016X}")
    print(f"Key       : 0x{key:016X}")
    print(f"Round Keys: {[f'0x{k:04X}' for k in round_keys]}")

    ciphertext = lsa_encrypt(plaintext, round_keys)
    decrypted = lsa_decrypt(ciphertext, round_keys)

    print(f"Ciphertext: 0x{ciphertext:016X}")
    print(f"Decrypted : 0x{decrypted:016X}")
    print(f"Match     : {'PASS' if decrypted == plaintext else 'FAIL'}")
    print()


def print_table_i():
    """Print Table I: Algorithm Comparison."""
    print("=" * 60)
    print("TABLE I: Algorithm Comparison")
    print("=" * 60)
    print(f"{'Parameter':<25} {'LSA':<15} {'SPN':<15} {'Feistel':<15}")
    print("-" * 70)
    print(f"{'Block Size':<25} {'64 bits':<15} {'64 bits':<15} {'64 bits':<15}")
    print(f"{'Key Size':<25} {'64 bits':<15} {'Variable':<15} {'Variable':<15}")
    print(f"{'Number of Rounds':<25} {'5':<15} {'5+':<15} {'8+':<15}")
    print(f"{'Sub-block Size':<25} {'16 bits':<15} {'16 bits':<15} {'32 bits':<15}")
    print(f"{'Segment Size':<25} {'4 bits':<15} {'4 bits':<15} {'4 bits':<15}")
    print(f"{'Key Expansion':<25} {'SIT-based':<15} {'Linear':<15} {'Linear':<15}")
    print(f"{'Key Management':<25} {'SPINS-based':<15} {'None':<15} {'None':<15}")
    print()


def save_results_to_json(results: dict, path: str = "results/simulation_results.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[Save] Results saved to {path}")


def save_results_to_csv(results: dict, path: str = "results/simulation_results.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Algorithm", "X", "Value"])
        for metric, alg_data in results.items():
            for alg, data in alg_data.items():
                for x_val, y_val in data.items():
                    writer.writerow([metric, alg, x_val, f"{y_val:.4f}"])
    print(f"[Save] CSV saved to {path}")


def run_all_simulations():
    """Orchestrate all simulations and generate outputs."""
    print("=" * 60)
    print("LSA Research Reproduction — Simulation Runner")
    print("=" * 60)
    print()

    sanity_check_cipher()
    print_table_i()

    os.makedirs("results", exist_ok=True)

    algorithms = ["lsa", "spn", "feistel"]
    all_results = {
        "key_expansion_time_ms": {},
        "security_level_percent": {},
        "energy_consumption_uj": {},
        "pdr_percent": {},
    }

    # ------------------------------------------------------------------
    # 1. Key Expansion Time
    # ------------------------------------------------------------------
    print("[Sim] Measuring Key Expansion Time ...")
    for alg in algorithms:
        print(f"      -> {alg.upper()}")
        all_results["key_expansion_time_ms"][alg] = measure_key_expansion_time(alg)
    print()

    # ------------------------------------------------------------------
    # 2. Security Level
    # ------------------------------------------------------------------
    print("[Sim] Measuring Security Level ...")
    for alg in algorithms:
        print(f"      -> {alg.upper()}")
        all_results["security_level_percent"][alg] = measure_security_level(alg)
    print()

    # ------------------------------------------------------------------
    # 3. Energy Consumption
    # ------------------------------------------------------------------
    print("[Sim] Measuring Energy Consumption ...")
    for alg in algorithms:
        print(f"      -> {alg.upper()}")
        all_results["energy_consumption_uj"][alg] = measure_energy_consumption(alg)
    print()

    # ------------------------------------------------------------------
    # 4. Packet Delivery Ratio
    # ------------------------------------------------------------------
    print("[Sim] Measuring Packet Delivery Ratio ...")
    for alg in algorithms:
        print(f"      -> {alg.upper()}")
        all_results["pdr_percent"][alg] = measure_pdr(alg)
    print()

    # ------------------------------------------------------------------
    # Print numeric summary
    # ------------------------------------------------------------------
    print("=" * 60)
    print("NUMERIC SUMMARY")
    print("=" * 60)
    for metric, alg_data in all_results.items():
        print(f"\n{metric}:")
        for alg, data in alg_data.items():
            values = list(data.values())
            avg = sum(values) / len(values)
            print(f"  {alg.upper():<10} avg = {avg:.2f}  |  {data}")
    print()

    # ------------------------------------------------------------------
    # Generate Plots
    # ------------------------------------------------------------------
    print("[Plot] Generating publication-quality plots ...")
    plot_key_expansion(
        all_results["key_expansion_time_ms"]["lsa"],
        all_results["key_expansion_time_ms"]["spn"],
        all_results["key_expansion_time_ms"]["feistel"],
    )
    plot_security(
        all_results["security_level_percent"]["lsa"],
        all_results["security_level_percent"]["spn"],
        all_results["security_level_percent"]["feistel"],
    )
    plot_energy(
        all_results["energy_consumption_uj"]["lsa"],
        all_results["energy_consumption_uj"]["spn"],
        all_results["energy_consumption_uj"]["feistel"],
    )
    plot_pdr(
        all_results["pdr_percent"]["lsa"],
        all_results["pdr_percent"]["spn"],
        all_results["pdr_percent"]["feistel"],
    )
    print()

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    save_results_to_json(all_results)
    save_results_to_csv(all_results)

    print("=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print("Outputs:")
    print("  - results/plot_key_expansion.png")
    print("  - results/plot_security.png")
    print("  - results/plot_energy.png")
    print("  - results/plot_pdr.png")
    print("  - results/simulation_results.json")
    print("  - results/simulation_results.csv")


if __name__ == "__main__":
    run_all_simulations()
