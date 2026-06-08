"""
LSA v2.0 Constants
==================
Updated tables for enhanced diffusion and security.
"""

from typing import List

# =============================================================================
# S-Box: 4-bit input -> 4-bit output (bijective)
# Derived from PRESENT S-Box for proven differential properties
# =============================================================================
S_BOX: List[int] = [
    0xE, 0x4, 0xD, 0x1,
    0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC,
    0x5, 0x9, 0x0, 0x7,
]

INV_S_BOX: List[int] = [0] * 16
for _i, _v in enumerate(S_BOX):
    INV_S_BOX[_v] = _i

# =============================================================================
# P-Table v2: Enhanced 16-bit permutation for better diffusion
# Designed to increase avalanche effect after 3 rounds
# =============================================================================
P_TABLE: List[int] = [
    15, 11, 7, 3,
    14, 10, 6, 2,
    13, 9, 5, 1,
    12, 8, 4, 0,
]

# Additional P-Table layer for v2 enhanced f-function
P_TABLE_V2: List[int] = [
    10, 14, 2, 6,
    0, 12, 8, 4,
    15, 11, 3, 7,
    1, 13, 9, 5,
]

INV_P_TABLE: List[int] = [0] * 16
for _i, _v in enumerate(P_TABLE):
    INV_P_TABLE[_v] = _i

INV_P_TABLE_V2: List[int] = [0] * 16
for _i, _v in enumerate(P_TABLE_V2):
    INV_P_TABLE_V2[_v] = _i

# =============================================================================
# Q-Table: 16-bit transposition (nibble positions)
# =============================================================================
Q_TABLE: List[int] = [3, 1, 0, 2]

INV_Q_TABLE: List[int] = [0] * 4
for _i, _v in enumerate(Q_TABLE):
    INV_Q_TABLE[_v] = _i

# =============================================================================
# Mode Configuration
# =============================================================================

class LSAMode:
    """LSA operation mode configuration."""
    LEGACY = "legacy"   # 64-bit key, 5 rounds (original paper)
    V2 = "v2"           # 128-bit key, 8 rounds (upgraded)

# Default mode
DEFAULT_MODE = LSAMode.V2

# Key sizes and round counts
KEY_SIZE_LEGACY = 64
NUM_ROUNDS_LEGACY = 5
KEY_SIZE_V2 = 128
NUM_ROUNDS_V2 = 8
BLOCK_SIZE = 64
SUB_BLOCK_SIZE = 16
SEGMENT_SIZE = 4
