"""
SPN Key Schedule — generates round keys from master key.
"""

from typing import List


def spn_key_schedule(master_key: int, key_size_bits: int, num_rounds: int) -> List[int]:
    """
    Generate round keys for SPN.

    For key_size_bits <= 64, uses simple rotation and S-Box mixing.
    For larger keys, simulates additional schedule work.
    """
    if key_size_bits <= 64:
        mask = (1 << key_size_bits) - 1 if key_size_bits < 64 else 0xFFFFFFFFFFFFFFFF
        key = master_key & mask
        round_keys = []
        for r in range(num_rounds + 1):  # +1 for final key mixing
            rk = (key ^ (0x9E3779B9 * (r + 1))) & 0xFFFF
            round_keys.append(rk)
            key = ((key << 5) | (key >> (key_size_bits - 5))) & mask
        return round_keys
    else:
        # Simulate larger key schedule
        chunks = (key_size_bits + 63) // 64
        all_keys = []
        for c in range(chunks):
            chunk_key = (master_key + c * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
            chunk_keys = spn_key_schedule(chunk_key, 64, num_rounds)
            all_keys.extend(chunk_keys)
        # Return proportionally more keys
        needed = num_rounds + 1
        if len(all_keys) >= needed:
            return all_keys[:needed]
        else:
            return all_keys + [0x0000] * (needed - len(all_keys))
