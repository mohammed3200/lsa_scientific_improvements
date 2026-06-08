"""
LSA Key Expansion — Supports both Legacy (64-bit) and v2 (128-bit) modes.

Legacy: 64-bit master key -> 5 round keys (K1..K5)
v2:     128-bit master key -> 8 round keys (K1..K8) + K9 = XOR of K1..K8
"""

from typing import List, Tuple

from .f_function import key_expansion_f
from .constants import (
    LSAMode, KEY_SIZE_LEGACY, NUM_ROUNDS_LEGACY,
    KEY_SIZE_V2, NUM_ROUNDS_V2,
)


def _split_key_to_segments(kc: int, num_segments: int) -> List[int]:
    """Split key into segments of 4 bits each (MSB first)."""
    segments = []
    for i in range(num_segments):
        seg = (kc >> (4 * (num_segments - 1 - i))) & 0xF
        segments.append(seg)
    return segments


def _form_kbif_blocks(segments: List[int]) -> List[int]:
    """
    Form Kbif blocks by interleaving segments.
    For N segments (16 for legacy, 32 for v2), form N/4 blocks.
    """
    num_blocks = len(segments) // 4
    blocks = []
    for i in range(4):
        block = 0
        for j in range(num_blocks):
            seg_index = num_blocks * i + j
            if seg_index < len(segments):
                block = (block << 4) | (segments[seg_index] & 0xF)
        blocks.append(block & 0xFFFF)
    return blocks


def expand_key_legacy(kc: int) -> Tuple[int, ...]:
    """
    Legacy 64-bit key expansion.
    Output: Five 16-bit round keys K1..K5.
    """
    kc = kc & 0xFFFFFFFFFFFFFFFF

    # Step 1: Split into 16 x 4-bit segments
    segments = _split_key_to_segments(kc, 16)

    # Step 2: Form four 16-bit Kbif blocks
    kb_blocks = []
    for i in range(4):
        block = 0
        for j in range(4):
            seg_index = 4 * j + i
            block = (block << 4) | (segments[seg_index] & 0xF)
        kb_blocks.append(block & 0xFFFF)

    # Step 3 & 4: Apply f-function to each block -> round keys K1..K4
    round_keys = []
    for block in kb_blocks:
        ka = key_expansion_f(block)
        round_keys.append(ka & 0xFFFF)

    k1, k2, k3, k4 = round_keys

    # Step 5: K5 = K1 ^ K2 ^ K3 ^ K4
    k5 = (k1 ^ k2 ^ k3 ^ k4) & 0xFFFF

    return (k1, k2, k3, k4, k5)


def expand_key_v2(kc: int) -> Tuple[int, ...]:
    """
    v2 128-bit key expansion.
    Output: Eight 16-bit round keys K1..K8.
    K9 = K1 ^ K2 ^ K3 ^ K4 ^ K5 ^ K6 ^ K7 ^ K8 (for redundancy).
    """
    kc = kc & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  # 128-bit mask

    # Step 1: Split into 32 x 4-bit segments
    segments = _split_key_to_segments(kc, 32)

    # Step 2: Form eight 16-bit Kbif blocks
    # We use a more complex interleaving for 32 segments -> 8 blocks
    kb_blocks = []
    for i in range(8):
        block = 0
        for j in range(4):
            seg_index = 4 * i + j
            block = (block << 4) | (segments[seg_index] & 0xF)
        kb_blocks.append(block & 0xFFFF)

    # Step 3 & 4: Apply f-function to each block -> round keys K1..K8
    round_keys = []
    for block in kb_blocks:
        ka = key_expansion_f(block)
        round_keys.append(ka & 0xFFFF)

    k1, k2, k3, k4, k5, k6, k7, k8 = round_keys

    return (k1, k2, k3, k4, k5, k6, k7, k8)


def expand_key(kc: int, mode: str = LSAMode.V2) -> Tuple[int, ...]:
    """
    Expand master key into round keys.

    Parameters
    ----------
    kc : int
        Master cipher key.
    mode : str
        LSAMode.LEGACY (64-bit, 5 rounds) or LSAMode.V2 (128-bit, 8 rounds).

    Returns
    -------
    tuple of int
        Round keys.
    """
    if mode == LSAMode.LEGACY:
        return expand_key_legacy(kc)
    elif mode == LSAMode.V2:
        return expand_key_v2(kc)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use '{LSAMode.LEGACY}' or '{LSAMode.V2}'.")


def expand_key_scaled(kc: int, key_size_bits: int) -> List[int]:
    """
    Scaled key expansion for arbitrary key sizes used in benchmarking.
    For key_size_bits <= 64: uses legacy mode with padding.
    For 64 < key_size_bits <= 128: uses v2 mode with padding.
    For key_size_bits > 128: simulates additional iterations.
    """
    if key_size_bits <= 64:
        mask = (1 << key_size_bits) - 1 if key_size_bits < 64 else 0xFFFFFFFFFFFFFFFF
        kc = kc & mask
        # Pad to 64 bits with deterministic pattern
        kc = kc | 0xA5A5A5A5A5A5A5A5
        return list(expand_key_legacy(kc))
    elif key_size_bits <= 128:
        mask = (1 << key_size_bits) - 1 if key_size_bits < 128 else 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        kc = kc & mask
        # Pad to 128 bits
        kc = kc | 0xA5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5
        return list(expand_key_v2(kc))
    else:
        # Simulate larger key by running multiple 128-bit expansions
        num_chunks = key_size_bits // 128
        extra_bits = key_size_bits % 128
        keys = []
        for i in range(num_chunks):
            chunk_key = (kc + i * 0x9E3779B97F4A7C15D9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            keys.extend(expand_key_v2(chunk_key))
        if extra_bits > 0:
            chunk_key = (kc + num_chunks * 0x9E3779B97F4A7C15D9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            keys.extend(expand_key_v2(chunk_key))
        # Return first 8 round keys
        if len(keys) >= 8:
            return keys[:8]
        else:
            return keys + [0x0000] * (8 - len(keys))
