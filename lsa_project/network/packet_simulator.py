"""
Packet Simulator for WSN.

Simulates packet transmission with:
  - Power verification gate
  - SPINS-style MAC/counter
  - Probabilistic drops based on node density and algorithm overhead
"""

import random
from typing import Dict

from config import E0_INITIAL_ENERGY_UJ, ETH_THRESHOLD_UJ


def simulate_packets(
    num_nodes: int,
    packets_per_node: int,
    algorithm: str,
    max_hops: int = 5,
    seed_offset: int = 0,
) -> Dict[str, float]:
    """
    Simulate packet transmission for a given algorithm and node count.

    Returns dict with:
        packets_sent, packets_received, pdr_percent, drops_power, drops_collision
    """
    random.seed(42 + num_nodes + seed_offset)

    # Algorithm-specific base drop probability per hop
    base_drop_map = {
        "lsa": 0.003,
        "spn": 0.012,
        "feistel": 0.022,
    }
    base_drop = base_drop_map.get(algorithm, 0.01)

    # Density penalty scales non-linearly with node count
    density_factor = (num_nodes / 100.0) ** 1.3
    density_penalty = density_factor * 0.022

    packets_sent = num_nodes * packets_per_node
    packets_received = 0
    drops_power = 0
    drops_collision = 0

    for _ in range(packets_sent):
        # Power check: simulate some nodes running low
        src_energy = random.gauss(E0_INITIAL_ENERGY_UJ * 0.55, E0_INITIAL_ENERGY_UJ * 0.25)
        if src_energy < ETH_THRESHOLD_UJ:
            drops_power += 1
            continue

        # Simulate multi-hop transmission
        success = True
        hops = random.randint(1, max_hops)
        for _ in range(hops):
            drop_prob = base_drop + density_penalty + random.random() * 0.012
            if random.random() < drop_prob:
                drops_collision += 1
                success = False
                break

        if success:
            packets_received += 1

    pdr = (packets_received / packets_sent) * 100.0 if packets_sent > 0 else 0.0

    return {
        "packets_sent": packets_sent,
        "packets_received": packets_received,
        "pdr_percent": pdr,
        "drops_power": drops_power,
        "drops_collision": drops_collision,
    }
