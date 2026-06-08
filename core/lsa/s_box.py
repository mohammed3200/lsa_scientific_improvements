"""
S-Box and inverse S-Box for LSA v2.0.
Includes constant-time lookup to mitigate timing side-channels.
"""

from typing import List

from .constants import S_BOX, INV_S_BOX


def apply_s_box_nibble(nibble: int) -> int:
    """Apply S-Box to a single 4-bit nibble."""
    return S_BOX[nibble & 0xF]


def apply_inv_s_box_nibble(nibble: int) -> int:
    """Apply inverse S-Box to a single 4-bit nibble."""
    return INV_S_BOX[nibble & 0xF]


def apply_s_box_16bit(value: int) -> int:
    """Apply S-Box to each nibble of a 16-bit value."""
    value = value & 0xFFFF
    n0 = (value >> 12) & 0xF
    n1 = (value >> 8) & 0xF
    n2 = (value >> 4) & 0xF
    n3 = value & 0xF
    return (
        (S_BOX[n0] << 12)
        | (S_BOX[n1] << 8)
        | (S_BOX[n2] << 4)
        | S_BOX[n3]
    ) & 0xFFFF


def apply_inv_s_box_16bit(value: int) -> int:
    """Apply inverse S-Box to each nibble of a 16-bit value."""
    value = value & 0xFFFF
    n0 = (value >> 12) & 0xF
    n1 = (value >> 8) & 0xF
    n2 = (value >> 4) & 0xF
    n3 = value & 0xF
    return (
        (INV_S_BOX[n0] << 12)
        | (INV_S_BOX[n1] << 8)
        | (INV_S_BOX[n2] << 4)
        | INV_S_BOX[n3]
    ) & 0xFFFF


def constant_time_sbox_lookup(value: int) -> int:
    """
    Constant-time S-Box lookup for a 4-bit value.
    Uses bitwise masking to prevent timing side-channels.
    No array indexing that depends on secret values.

    Parameters
    ----------
    value : int
        4-bit input (0-15).

    Returns
    -------
    int
        4-bit S-Box output.
    """
    value = value & 0xF
    result = 0
    for i in range(16):
        # Constant-time comparison: mask = 0xF if value == i else 0
        mask = -((value ^ i) == 0) & 0xF
        result |= mask & S_BOX[i]
    return result & 0xF


def apply_s_box_16bit_constant_time(value: int) -> int:
    """
    Apply constant-time S-Box to each nibble of a 16-bit value.
    """
    value = value & 0xFFFF
    n0 = (value >> 12) & 0xF
    n1 = (value >> 8) & 0xF
    n2 = (value >> 4) & 0xF
    n3 = value & 0xF
    return (
        (constant_time_sbox_lookup(n0) << 12)
        | (constant_time_sbox_lookup(n1) << 8)
        | (constant_time_sbox_lookup(n2) << 4)
        | constant_time_sbox_lookup(n3)
    ) & 0xFFFF
