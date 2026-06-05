"""
Analytical Energy Consumption Model for WSN.

Uses the First Order Radio Model to derive energy analytically
and validate against simulation results.
"""

import math
from typing import Dict, Any


# Radio model constants (typical IEEE 802.15.4 values)
E_ELEC_NJ_PER_BIT = 50.0       # nJ/bit for transmitter/receiver electronics
E_AMP_NJ_PER_BIT_M2 = 0.1      # nJ/bit/m² for transmit amplifier
E_FS_NJ_PER_BIT_M4 = 0.0013    # nJ/bit/m⁴ for free-space model (not used here)


def encryption_energy_nj() -> float:
    """
    Estimate encryption energy per 64-bit block.
    Based on ~75 arithmetic operations at 1 nJ per operation.
    """
    ops = 75  # from complexity analysis
    return ops * 1.0  # nJ per operation heuristic


def transmission_energy(k_bits: int, distance_m: float) -> float:
    """
    First Order Radio Model: E_tx = E_elec * k + E_amp * k * d².

    Returns energy in nJ.
    """
    return E_ELEC_NJ_PER_BIT * k_bits + E_AMP_NJ_PER_BIT_M2 * k_bits * (distance_m ** 2)


def reception_energy(k_bits: int) -> float:
    """
    Reception energy: E_rx = E_elec * k.

    Returns energy in nJ.
    """
    return E_ELEC_NJ_PER_BIT * k_bits


def total_network_energy(
    n_nodes: int,
    packets_per_node: int,
    packet_bits: int = 512,
    avg_distance_m: float = 30.0,
    algorithm_overhead: float = 1.0,
) -> Dict[str, Any]:
    """
    Compute total network energy analytically.

    Parameters
    ----------
    n_nodes : int
        Number of sensor nodes.
    packets_per_node : int
        Packets sent per node.
    packet_bits : int
        Packet size in bits.
    avg_distance_m : float
        Average transmission distance.
    algorithm_overhead : float
        Multiplier for encryption energy (LSA=1.0, SPN=2.0, Feistel=2.1).

    Returns
    -------
    dict
        Total energy in μJ, broken down by component.
    """
    total_packets = n_nodes * packets_per_node
    total_bits = total_packets * packet_bits

    # TX + RX energy (nJ)
    tx_nj = transmission_energy(total_bits, avg_distance_m)
    rx_nj = reception_energy(total_bits)

    # Encryption energy (nJ)
    blocks = total_bits / 64.0
    enc_nj = blocks * encryption_energy_nj() * algorithm_overhead

    total_nj = tx_nj + rx_nj + enc_nj
    total_uj = total_nj / 1000.0

    return {
        "n_nodes": n_nodes,
        "packets_per_node": packets_per_node,
        "total_energy_uj": total_uj,
        "tx_energy_uj": tx_nj / 1000.0,
        "rx_energy_uj": rx_nj / 1000.0,
        "enc_energy_uj": enc_nj / 1000.0,
    }


def validate_model(simulated_values: Dict[int, float], analytical_values: Dict[int, float]) -> Dict[int, float]:
    """Return error % between analytical model and simulation per node count."""
    errors = {}
    for n in simulated_values:
        if n in analytical_values and analytical_values[n] != 0:
            errors[n] = abs(simulated_values[n] - analytical_values[n]) / analytical_values[n] * 100.0
        else:
            errors[n] = 0.0
    return errors
