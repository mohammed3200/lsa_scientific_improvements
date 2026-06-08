"""
LSA v2 Encryption — 8-Round Hybrid Block Cipher with Enhanced f-function.

Input : 64-bit plaintext block, round keys K1..K8 (128-bit master key)
Output: 64-bit ciphertext block

Enhancements over Legacy:
- 8 rounds instead of 5 (≥16 active S-boxes per differential trail)
- Enhanced f-function with additional P-Table layer and 12-bit rotation
- Full avalanche after 3 rounds (vs 5 in Legacy)
"""

from typing import Tuple

from .f_function import encrypt_f_v2, decrypt_f_v2


def _split_64_to_16(value: int) -> Tuple[int, int, int, int]:
    """Split 64-bit value into four 16-bit sub-blocks (MSB first)."""
    value = value & 0xFFFFFFFFFFFFFFFF
    p1 = (value >> 48) & 0xFFFF
    p2 = (value >> 32) & 0xFFFF
    p3 = (value >> 16) & 0xFFFF
    p4 = value & 0xFFFF
    return p1, p2, p3, p4


def _combine_16_to_64(p1: int, p2: int, p3: int, p4: int) -> int:
    """Combine four 16-bit sub-blocks into a 64-bit value."""
    return (
        ((p1 & 0xFFFF) << 48)
        | ((p2 & 0xFFFF) << 32)
        | ((p3 & 0xFFFF) << 16)
        | (p4 & 0xFFFF)
    ) & 0xFFFFFFFFFFFFFFFF


def _xnor_16(a: int, b: int) -> int:
    """16-bit XNOR: ~(a ^ b) & 0xFFFF."""
    return (~(a ^ b)) & 0xFFFF


def _xor_16(a: int, b: int) -> int:
    """16-bit XOR."""
    return (a ^ b) & 0xFFFF


def lsa_encrypt_v2(plaintext: int, round_keys: Tuple[int, ...]) -> int:
    """
    Encrypt a 64-bit plaintext block using LSA v2 (8 rounds).

    Parameters
    ----------
    plaintext : int
        64-bit plaintext block.
    round_keys : tuple of int
        (K1, K2, K3, K4, K5, K6, K7, K8) each 16-bit.

    Returns
    -------
    int
        64-bit ciphertext block.
    """
    plaintext = plaintext & 0xFFFFFFFFFFFFFFFF

    p1, p2, p3, p4 = _split_64_to_16(plaintext)

    for i in range(8):
        ki = round_keys[i] & 0xFFFF

        # Left side: P1 XNOR Ki -> enhanced f-function -> EFL
        r1_1 = _xnor_16(p1, ki)
        efl = encrypt_f_v2(r1_1) & 0xFFFF

        # Right side: P4 XNOR Ki -> enhanced f-function -> EFR
        r1_4 = _xnor_16(p4, ki)
        efr = encrypt_f_v2(r1_4) & 0xFFFF

        # Middle blocks: P2 XOR EFL, P3 XOR EFR
        r1_2 = _xor_16(p2, efl)
        r1_3 = _xor_16(p3, efr)

        # Swapping between internal pairs
        p1, p2 = r1_2, r1_1
        p3, p4 = r1_4, r1_3

    ciphertext = _combine_16_to_64(p1, p2, p3, p4)
    return ciphertext


def lsa_decrypt_v2(ciphertext: int, round_keys: Tuple[int, ...]) -> int:
    """
    Decrypt a 64-bit ciphertext block using LSA v2.
    Uses round keys in reverse order (K8 -> K1).
    """
    ciphertext = ciphertext & 0xFFFFFFFFFFFFFFFF

    p1, p2, p3, p4 = _split_64_to_16(ciphertext)

    for i in range(7, -1, -1):
        ki = round_keys[i] & 0xFFFF

        # Undo swapping
        r1_1 = p2
        r1_2 = p1
        r1_3 = p4
        r1_4 = p3

        # Recover P2 and P3
        efl = encrypt_f_v2(r1_1) & 0xFFFF
        efr = encrypt_f_v2(r1_4) & 0xFFFF
        p2 = _xor_16(r1_2, efl)
        p3 = _xor_16(r1_3, efr)

        # Recover P1 and P4
        p1 = _xnor_16(r1_1, ki)
        p4 = _xnor_16(r1_4, ki)

    plaintext = _combine_16_to_64(p1, p2, p3, p4)
    return plaintext
