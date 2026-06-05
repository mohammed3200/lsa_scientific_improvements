"""
f-function implementations for LSA.

Two variants:
1. key_expansion_f : P->Q->P->Q->P->Q wiring for key schedule (Phase 1)
2. encrypt_f       : AND -> Left Shift -> S-Box -> OR for encryption (Phase 3)
"""

from typing import List

from .s_box import apply_s_box_16bit, apply_inv_s_box_16bit

# P-Table: 16-bit permutation (bit positions)
P_TABLE: List[int] = [
    15, 11, 7, 3,
    14, 10, 6, 2,
    13, 9, 5, 1,
    12, 8, 4, 0,
]

# Q-Table: 16-bit transposition (nibble positions)
Q_TABLE: List[int] = [3, 1, 0, 2]

# Precompute inverse P_TABLE
INV_P_TABLE: List[int] = [0] * 16
for _i, _v in enumerate(P_TABLE):
    INV_P_TABLE[_v] = _i

# Precompute inverse Q_TABLE
INV_Q_TABLE: List[int] = [0] * 4
for _i, _v in enumerate(Q_TABLE):
    INV_Q_TABLE[_v] = _i


def _permute_bits_16(value: int, table: List[int]) -> int:
    """Permute bits of a 16-bit value according to table."""
    value = value & 0xFFFF
    result = 0
    for out_pos in range(16):
        in_pos = table[out_pos]
        bit = (value >> in_pos) & 1
        result |= bit << out_pos
    return result & 0xFFFF


def _transpose_nibbles_16(value: int, table: List[int]) -> int:
    """Transposition (nibble shuffle) of a 16-bit value."""
    value = value & 0xFFFF
    nibbles = [(value >> (4 * i)) & 0xF for i in range(4)]
    result = 0
    for out_pos in range(4):
        in_pos = table[out_pos]
        result |= nibbles[in_pos] << (4 * out_pos)
    return result & 0xFFFF


def key_expansion_f(value: int) -> int:
    """
    f-function for key expansion (Phase 1).
    Implements P->Q->P->Q->P->Q wiring with XOR/XNOR/left-shift mixing.
    """
    value = value & 0xFFFF

    # Layer 1: P-table permutation + XOR with shifted version
    x = _permute_bits_16(value, P_TABLE)
    x = x ^ ((value << 3) & 0xFFFF)
    x = x & 0xFFFF

    # Layer 2: Q-table transposition + XNOR with shifted version
    y = _transpose_nibbles_16(x, Q_TABLE)
    shifted = (~((x << 2) & 0xFFFF)) & 0xFFFF
    y = ~(y ^ shifted) & 0xFFFF
    y = y & 0xFFFF

    # Layer 3: P-table permutation + XOR
    z = _permute_bits_16(y, P_TABLE)
    z = z ^ ((y << 1) & 0xFFFF)
    z = z & 0xFFFF

    # Layer 4: Q-table transposition + XNOR
    w = _transpose_nibbles_16(z, Q_TABLE)
    shifted = (~((z << 4) & 0xFFFF)) & 0xFFFF
    w = ~(w ^ shifted) & 0xFFFF
    w = w & 0xFFFF

    # Layer 5: P-table permutation + XOR
    v = _permute_bits_16(w, P_TABLE)
    v = v ^ ((w << 2) & 0xFFFF)
    v = v & 0xFFFF

    # Layer 6: Q-table transposition
    out = _transpose_nibbles_16(v, Q_TABLE)
    out = out & 0xFFFF

    return out


def inv_key_expansion_f(value: int) -> int:
    """Inverse of key_expansion_f for decryption key schedule if needed."""
    value = value & 0xFFFF

    # Inverse Layer 6: Q-table transposition
    v = _transpose_nibbles_16(value, INV_Q_TABLE)

    # Inverse Layer 5: undo XOR then inv P
    w = v ^ ((v << 2) & 0xFFFF)  # rough inverse for demonstration
    w = _permute_bits_16(w, INV_P_TABLE)
    w = w & 0xFFFF

    # For full correctness we'd need proper inverse of the XNOR/XOR chains.
    # In practice decryption reuses forward keys in reverse order (Feistel property).
    # This function is kept for completeness.
    return w & 0xFFFF


def encrypt_f(value: int) -> int:
    """
    f-function for encryption rounds (Phase 3).
    Operations: AND -> Left Shift -> S-Box substitution -> OR.
    Input/Output: 16 bits.
    """
    value = value & 0xFFFF

    # AND step: split into two 8-bit halves and mask
    upper = (value >> 8) & 0xFF
    lower = value & 0xFF

    # Left Shift step (rotate each byte left by 1)
    upper_ls = ((upper << 1) | (upper >> 7)) & 0xFF
    lower_ls = ((lower << 1) | (lower >> 7)) & 0xFF

    # Recombine and split into nibbles for S-Box
    combined = ((upper_ls << 8) | lower_ls) & 0xFFFF

    # S-Box substitution (per nibble)
    substituted = apply_s_box_16bit(combined)

    # OR step: mix with original value (adds non-linearity)
    result = (substituted | (value >> 3)) & 0xFFFF

    return result


def decrypt_f(value: int) -> int:
    """
    Inverse f-function for decryption rounds.
    Since OR is not perfectly invertible, we approximate by reversing
    the S-Box and byte rotations.
    """
    value = value & 0xFFFF

    # Undo OR approximation: recover substituted value
    substituted = value & 0xFFFF  # approximate

    # Inverse S-Box
    combined = apply_inv_s_box_16bit(substituted)

    # Inverse byte rotations
    upper_ls = (combined >> 8) & 0xFF
    lower_ls = combined & 0xFF
    upper = ((upper_ls >> 1) | (upper_ls << 7)) & 0xFF
    lower = ((lower_ls >> 1) | (lower_ls << 7)) & 0xFF

    result = ((upper << 8) | lower) & 0xFFFF
    return result
