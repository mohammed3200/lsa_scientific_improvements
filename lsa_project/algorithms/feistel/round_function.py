"""
Feistel round function using S-Box substitution and bit permutation.
"""

from typing import List

# Reuse LSA S-Box
S_BOX = [
    0xE, 0x4, 0xD, 0x1,
    0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC,
    0x5, 0x9, 0x0, 0x7,
]

# 32-bit permutation table
PERM32 = list(range(32))
for i in range(0, 32, 4):
    PERM32[i], PERM32[i + 2] = PERM32[i + 2], PERM32[i]

INV_PERM32 = [0] * 32
for _i, _v in enumerate(PERM32):
    INV_PERM32[_v] = _i


def _permute_32(value: int, table: List[int]) -> int:
    result = 0
    for out_pos in range(32):
        in_pos = table[out_pos]
        bit = (value >> in_pos) & 1
        result |= bit << out_pos
    return result & 0xFFFFFFFF


def _sub_bytes_32(value: int) -> int:
    result = 0
    for i in range(8):
        nibble = (value >> (4 * i)) & 0xF
        result |= S_BOX[nibble] << (4 * i)
    return result & 0xFFFFFFFF


def feistel_round_function(right_half: int, round_key: int) -> int:
    """
    Feistel round function F(R, K).
    Input : 32-bit right half, 32-bit expanded round key
    Output: 32-bit transformed value
    """
    right_half = right_half & 0xFFFFFFFF
    round_key = round_key & 0xFFFFFFFF

    # Key mixing
    x = right_half ^ round_key

    # Substitution
    x = _sub_bytes_32(x)

    # Permutation
    x = _permute_32(x, PERM32)

    # Additional mixing
    x = x ^ ((round_key >> 16) | (round_key << 16)) & 0xFFFFFFFF

    return x & 0xFFFFFFFF
