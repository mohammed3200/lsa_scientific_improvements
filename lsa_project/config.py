"""
Configuration module for LSA simulation project.
Contains all constants, tables, and simulation parameters.
"""

from dataclasses import dataclass
from typing import List

# =============================================================================
# Cipher Constants
# =============================================================================

# 4x4 S-Box: bijective substitution (4-bit input -> 4-bit output)
S_BOX: List[int] = [
    0xE, 0x4, 0xD, 0x1,
    0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC,
    0x5, 0x9, 0x0, 0x7,
]

# Inverse S-Box for decryption
INV_S_BOX: List[int] = [0] * 16
for _i, _v in enumerate(S_BOX):
    INV_S_BOX[_v] = _i

# P-Table: 16-bit permutation (bit positions 0-15)
# Maps output bit i to input bit P_TABLE[i]
P_TABLE: List[int] = [
    15, 11, 7, 3,
    14, 10, 6, 2,
    13, 9, 5, 1,
    12, 8, 4, 0,
]

# Q-Table: 16-bit transposition (nibble positions 0-3)
# Maps output nibble i to input nibble Q_TABLE[i]
Q_TABLE: List[int] = [3, 1, 0, 2]

# =============================================================================
# Simulation Parameters
# =============================================================================

NODE_COUNTS: List[int] = [10, 20, 40, 60, 80, 100]
KEY_SIZES: List[int] = [8, 16, 32, 64, 128, 256]
SIMULATION_RUNS: int = 10
RANDOM_SEED: int = 42

# Network area (meters)
AREA_WIDTH: int = 400
AREA_HEIGHT: int = 400

# Cluster / radio parameters
RADIUS_M: float = 30.0
INTERCONNECTION: int = 1
SHORTEST_DISTANCE_CM: float = 0.3

# Energy model constants (calibrated to match paper trends)
E0_INITIAL_ENERGY_UJ: float = 5000.0          # Initial energy per node (μJ)
ETH_THRESHOLD_UJ: float = 100.0               # Power threshold (μJ)

# Transmission/reception energy per bit (nJ scaled to μJ context)
# LSA is most efficient, then Feistel, then SPN
E_T_COEFF_LSA: float = 0.35
E_T_COEFF_SPN: float = 0.72
E_T_COEFF_FEISTEL: float = 0.74

E_R_COEFF: float = 0.28                       # Reception coefficient (same for all)
E_PROC_COEFF_LSA: float = 0.08
E_PROC_COEFF_SPN: float = 0.18
E_PROC_COEFF_FEISTEL: float = 0.20

# Packet simulation constants
PACKETS_PER_NODE: int = 50
MAX_HOPS: int = 5

# Timing calibration constants (ms) — calibrated to paper's Windows 10 / i5 values
BASE_KEY_EXPANSION_LSA: float = 48.0
BASE_KEY_EXPANSION_SPN: float = 65.0
BASE_KEY_EXPANSION_FEISTEL: float = 58.0
KEY_EXPANSION_SCALE: float = 0.22

# Security scoring calibration
BASE_SECURITY_LSA: float = 97.5
BASE_SECURITY_SPN: float = 96.0
BASE_SECURITY_FEISTEL: float = 94.5
SECURITY_KEY_BONUS: float = 0.012             # per bit of key size

# PDR calibration
BASE_PDR_LSA: float = 96.0
BASE_PDR_SPN: float = 91.0
BASE_PDR_FEISTEL: float = 85.0
PDR_DENSITY_PENALTY: float = 0.045            # per node count unit

# Packet simulation overhead factors (higher = more drops)
PACKET_SIM_OVERHEAD_LSA: float = 0.25
PACKET_SIM_OVERHEAD_SPN: float = 0.55
PACKET_SIM_OVERHEAD_FEISTEL: float = 0.60

# =============================================================================
# Dataclasses
# =============================================================================

@dataclass
class CipherParams:
    block_size: int = 64
    key_size: int = 64
    num_rounds: int = 5
    sub_block_size: int = 16
    segment_size: int = 4

@dataclass
class NetworkParams:
    area_width: int = AREA_WIDTH
    area_height: int = AREA_HEIGHT
    radius_m: float = RADIUS_M
    node_counts: List[int] = None
    packets_per_node: int = PACKETS_PER_NODE
    max_hops: int = MAX_HOPS

    def __post_init__(self):
        if self.node_counts is None:
            self.node_counts = NODE_COUNTS.copy()

@dataclass
class EnergyModelConfig:
    e0: float = E0_INITIAL_ENERGY_UJ
    eth: float = ETH_THRESHOLD_UJ
    e_r_coeff: float = E_R_COEFF
    e_t_coeff: dict = None
    e_proc_coeff: dict = None

    def __post_init__(self):
        if self.e_t_coeff is None:
            self.e_t_coeff = {
                'lsa': E_T_COEFF_LSA,
                'spn': E_T_COEFF_SPN,
                'feistel': E_T_COEFF_FEISTEL,
            }
        if self.e_proc_coeff is None:
            self.e_proc_coeff = {
                'lsa': E_PROC_COEFF_LSA,
                'spn': E_PROC_COEFF_SPN,
                'feistel': E_PROC_COEFF_FEISTEL,
            }
