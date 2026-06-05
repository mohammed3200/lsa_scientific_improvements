"""
S-Box and inverse S-Box definitions for LSA.
4-bit input -> 4-bit output (bijective).
"""

from typing import List

S_BOX: List[int] = [
    0xE, 0x4, 0xD, 0x1,
    0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC,
    0x5, 0x9, 0x0, 0x7,
]

INV_S_BOX: List[int] = [0] * 16
for _i, _v in enumerate(S_BOX):
    INV_S_BOX[_v] = _i


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
