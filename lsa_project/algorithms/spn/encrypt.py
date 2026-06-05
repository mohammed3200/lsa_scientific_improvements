"""
Lightweight SPN (Substitution-Permutation Network) baseline.

Block size: 64 bits
Key size  : variable (affects number of rounds)
Rounds    : 5 + (key_size_bits // 32) for fairness in comparison
"""

from typing import List, Tuple

from .key_schedule import spn_key_schedule

# Reuse LSA S-Box
S_BOX = [
    0xE, 0x4, 0xD, 0x1,
    0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC,
    0x5, 0x9, 0x0, 0x7,
]

INV_S_BOX = [0] * 16
for _i, _v in enumerate(S_BOX):
    INV_S_BOX[_v] = _i

# Bit permutation for 64-bit block: simple rotate-like shuffle
PERM_TABLE = list(range(64))
# Swap adjacent bit pairs in a structured way
for i in range(0, 64, 2):
    PERM_TABLE[i], PERM_TABLE[i + 1] = PERM_TABLE[i + 1], PERM_TABLE[i]

INV_PERM_TABLE = [0] * 64
for _i, _v in enumerate(PERM_TABLE):
    INV_PERM_TABLE[_v] = _i


def _permute_64(value: int, table: List[int]) -> int:
    result = 0
    for out_pos in range(64):
        in_pos = table[out_pos]
        bit = (value >> in_pos) & 1
        result |= bit << out_pos
    return result & 0xFFFFFFFFFFFFFFFF


def _sub_bytes_64(value: int) -> int:
    result = 0
    for i in range(16):
        nibble = (value >> (4 * i)) & 0xF
        result |= S_BOX[nibble] << (4 * i)
    return result & 0xFFFFFFFFFFFFFFFF


def _inv_sub_bytes_64(value: int) -> int:
    result = 0
    for i in range(16):
        nibble = (value >> (4 * i)) & 0xF
        result |= INV_S_BOX[nibble] << (4 * i)
    return result & 0xFFFFFFFFFFFFFFFF


def _num_rounds(key_size_bits: int) -> int:
    return 5 + (key_size_bits // 32)


def spn_encrypt(plaintext: int, master_key: int, key_size_bits: int = 64) -> int:
    """Encrypt 64-bit block with SPN."""
    plaintext = plaintext & 0xFFFFFFFFFFFFFFFF
    num_rounds = _num_rounds(key_size_bits)
    round_keys = spn_key_schedule(master_key, key_size_bits, num_rounds)

    state = plaintext
    for r in range(num_rounds):
        # Key mixing
        state = state ^ (round_keys[r] | (round_keys[r] << 16) | (round_keys[r] << 32) | (round_keys[r] << 48))
        state = state & 0xFFFFFFFFFFFFFFFF

        # Substitution
        state = _sub_bytes_64(state)

        # Permutation (not on last round)
        if r < num_rounds - 1:
            state = _permute_64(state, PERM_TABLE)

    # Final key mixing
    state = state ^ (round_keys[-1] | (round_keys[-1] << 16) | (round_keys[-1] << 32) | (round_keys[-1] << 48))
    return state & 0xFFFFFFFFFFFFFFFF


def spn_decrypt(ciphertext: int, master_key: int, key_size_bits: int = 64) -> int:
    """Decrypt 64-bit block with SPN."""
    ciphertext = ciphertext & 0xFFFFFFFFFFFFFFFF
    num_rounds = _num_rounds(key_size_bits)
    round_keys = spn_key_schedule(master_key, key_size_bits, num_rounds)

    state = ciphertext
    # Undo final key mixing
    state = state ^ (round_keys[-1] | (round_keys[-1] << 16) | (round_keys[-1] << 32) | (round_keys[-1] << 48))
    state = state & 0xFFFFFFFFFFFFFFFF

    for r in range(num_rounds - 1, -1, -1):
        # Undo permutation
        if r < num_rounds - 1:
            state = _permute_64(state, INV_PERM_TABLE)

        # Undo substitution
        state = _inv_sub_bytes_64(state)

        # Undo key mixing
        state = state ^ (round_keys[r] | (round_keys[r] << 16) | (round_keys[r] << 32) | (round_keys[r] << 48))
        state = state & 0xFFFFFFFFFFFFFFFF

    return state
