"""
Packet Delivery Ratio (PDR) metric.

PDR = (Packets Received / Packets Sent) * 100
"""

from typing import Dict

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NODE_COUNTS, SIMULATION_RUNS, PACKETS_PER_NODE, MAX_HOPS
from network.packet_simulator import simulate_packets


def measure_pdr(algorithm: str) -> Dict[int, float]:
    """
    Measure average Packet Delivery Ratio (%) for each node count.

    Returns {node_count: avg_pdr_percent}
    """
    results = {}
    for nc in NODE_COUNTS:
        pdrs = []
        for run in range(SIMULATION_RUNS):
            pkt_stats = simulate_packets(
                num_nodes=nc,
                packets_per_node=PACKETS_PER_NODE,
                algorithm=algorithm,
                max_hops=MAX_HOPS,
                seed_offset=run,
            )
            pdrs.append(pkt_stats["pdr_percent"])
        results[nc] = sum(pdrs) / len(pdrs)
    return results
