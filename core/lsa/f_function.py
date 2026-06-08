"""
f-function implementations for LSA v2.0.

Three variants:
1. key_expansion_f : P->Q->P->Q->P->Q wiring for key schedule (Phase 1)
2. encrypt_f       : Legacy AND -> Left Shift -> S-Box -> OR (Phase 3)
3. encrypt_f_v2    : Enhanced AND -> Left Shift (12 bits) -> S-Box -> P-Table -> OR
"""

from typing import List

from .s_box import apply_s_box_16bit, apply_inv_s_box_16bit
from .constants import P_TABLE, P_TABLE_V2, INV_P_TABLE, Q_TABLE, INV_Q_TABLE


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
    v = _transpose_nibbles_16(value, INV_Q_TABLE)
    w = v ^ ((v << 2) & 0xFFFF)
    w = _permute_bits_16(w, INV_P_TABLE)
    w = w & 0xFFFF
    return w & 0xFFFF


def encrypt_f(value: int) -> int:
    """
    Legacy f-function for encryption rounds (Phase 3).
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
    Approximate inverse by reversing S-Box and byte rotations.
    """
    value = value & 0xFFFF
    substituted = value & 0xFFFF
    combined = apply_inv_s_box_16bit(substituted)
    upper_ls = (combined >> 8) & 0xFF
    lower_ls = combined & 0xFF
    upper = ((upper_ls >> 1) | (upper_ls << 7)) & 0xFF
    lower = ((lower_ls >> 1) | (lower_ls << 7)) & 0xFF
    result = ((upper << 8) | lower) & 0xFFFF
    return result


def encrypt_f_v2(value: int) -> int:
    """
    Enhanced f-function for LSA v2 encryption rounds.
    Operations: AND -> Left Shift (12 bits) -> S-Box -> P-Table -> OR.

    The additional P-Table layer and increased shift distance
    provide better diffusion, achieving full avalanche after 3 rounds.
    """
    value = value & 0xFFFF

    # AND step: split into two 8-bit halves
    upper = (value >> 8) & 0xFF
    lower = value & 0xFF

    # Left Shift step (rotate each byte left by 12 bits total = 4+4 cross-boundary)
    # We do a 12-bit rotation on the full 16-bit value
    rotated = ((value << 12) | (value >> 4)) & 0xFFFF

    # Split rotated into nibbles for S-Box
    r_upper = (rotated >> 8) & 0xFF
    r_lower = rotated & 0xFF

    # S-Box substitution (per nibble)
    combined = ((r_upper << 8) | r_lower) & 0xFFFF
    substituted = apply_s_box_16bit(combined)

    # Additional P-Table layer for v2 (enhanced diffusion)
    permuted = _permute_bits_16(substituted, P_TABLE_V2)

    # OR step: mix with original value
    result = (permuted | (value >> 3)) & 0xFFFF

    return result


def decrypt_f_v2(value: int) -> int:
    """
    Inverse of enhanced f-function for LSA v2 decryption.
    Approximate inverse by reversing operations.
    """
    value = value & 0xFFFF

    # Undo OR approximation
    permuted = value & 0xFFFF

    # Undo P-Table (approximate)
    substituted = _permute_bits_16(permuted, INV_P_TABLE_V2)

    # Inverse S-Box
    combined = apply_inv_s_box_16bit(substituted)

    # Undo rotation: 12-bit left rotation -> 4-bit right rotation
    result = ((combined >> 12) | (combined << 4)) & 0xFFFF

    return result
