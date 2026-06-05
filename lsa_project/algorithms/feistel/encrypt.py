"""
Standard Feistel Network baseline.

Block size: 64 bits (split into two 32-bit halves)
Key size  : variable
Rounds    : 8 + (key_size_bits // 32)
"""

from typing import List

from .round_function import feistel_round_function


def _num_rounds(key_size_bits: int) -> int:
    return 8 + (key_size_bits // 32)


def _derive_round_keys(master_key: int, key_size_bits: int, num_rounds: int) -> List[int]:
    """Generate 32-bit round keys from master key."""
    if key_size_bits <= 64:
        mask = (1 << key_size_bits) - 1 if key_size_bits < 64 else 0xFFFFFFFFFFFFFFFF
        key = master_key & mask
        round_keys = []
        for r in range(num_rounds):
            rk = (key ^ (0x9E3779B9 * (r + 1))) & 0xFFFFFFFF
            round_keys.append(rk)
            key = ((key << 7) | (key >> (key_size_bits - 7))) & mask
        return round_keys
    else:
        chunks = (key_size_bits + 63) // 64
        all_keys = []
        for c in range(chunks):
            chunk_key = (master_key + c * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
            chunk_keys = _derive_round_keys(chunk_key, 64, num_rounds)
            all_keys.extend(chunk_keys)
        if len(all_keys) >= num_rounds:
            return all_keys[:num_rounds]
        else:
            return all_keys + [0x00000000] * (num_rounds - len(all_keys))


def feistel_encrypt(plaintext: int, master_key: int, key_size_bits: int = 64) -> int:
    """Encrypt 64-bit block with Feistel network."""
    plaintext = plaintext & 0xFFFFFFFFFFFFFFFF
    num_rounds = _num_rounds(key_size_bits)
    round_keys = _derive_round_keys(master_key, key_size_bits, num_rounds)

    left = (plaintext >> 32) & 0xFFFFFFFF
    right = plaintext & 0xFFFFFFFF

    for r in range(num_rounds):
        f_out = feistel_round_function(right, round_keys[r])
        new_left = right
        new_right = left ^ f_out
        left, right = new_left & 0xFFFFFFFF, new_right & 0xFFFFFFFF

    # Final swap is NOT undone in standard Feistel (or is it?)
    # Actually in standard Feistel, after last round we don't swap
    # But our loop above does swap every round. Let's undo the last swap.
    left, right = right, left

    return ((left & 0xFFFFFFFF) << 32) | (right & 0xFFFFFFFF)


def feistel_decrypt(ciphertext: int, master_key: int, key_size_bits: int = 64) -> int:
    """Decrypt 64-bit block with Feistel network."""
    ciphertext = ciphertext & 0xFFFFFFFFFFFFFFFF
    num_rounds = _num_rounds(key_size_bits)
    round_keys = _derive_round_keys(master_key, key_size_bits, num_rounds)

    left = (ciphertext >> 32) & 0xFFFFFFFF
    right = ciphertext & 0xFFFFFFFF

    # Reverse the final swap
    left, right = right, left

    for r in range(num_rounds - 1, -1, -1):
        f_out = feistel_round_function(left, round_keys[r])
        new_right = left
        new_left = right ^ f_out
        left, right = new_left & 0xFFFFFFFF, new_right & 0xFFFFFFFF

    return ((left & 0xFFFFFFFF) << 32) | (right & 0xFFFFFFFF)
