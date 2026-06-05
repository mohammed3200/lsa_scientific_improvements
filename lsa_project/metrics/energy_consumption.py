"""
Energy Consumption metric.

Computes total energy (μJ) vs number of nodes using the network energy model.
"""

from typing import Dict

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NODE_COUNTS, SIMULATION_RUNS, PACKETS_PER_NODE, MAX_HOPS
from network.packet_simulator import simulate_packets
from network.energy_model import compute_energy_consumption


def measure_energy_consumption(algorithm: str) -> Dict[int, float]:
    """
    Measure average total energy consumption (μJ) for each node count.

    Returns {node_count: avg_energy_uj}
    """
    results = {}
    for nc in NODE_COUNTS:
        energies = []
        for run in range(SIMULATION_RUNS):
            pkt_stats = simulate_packets(
                num_nodes=nc,
                packets_per_node=PACKETS_PER_NODE,
                algorithm=algorithm,
                max_hops=MAX_HOPS,
                seed_offset=run,
            )
            energy_stats = compute_energy_consumption(
                num_nodes=nc,
                packets_sent=pkt_stats["packets_sent"],
                packets_received=pkt_stats["packets_received"],
                algorithm=algorithm,
            )
            energies.append(energy_stats["total_energy_uj"])
        results[nc] = sum(energies) / len(energies)
    return results
