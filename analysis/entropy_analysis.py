"""
Key Space and Entropy Analysis for LSA.

Tests key collisions, Shannon entropy, and chi-square distribution.
"""

import math
import random
from collections import Counter
from typing import Dict, Any

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lsa_project"))

from algorithms.lsa.key_expansion import expand_key
from algorithms.lsa.encrypt import lsa_encrypt


def key_space_test(keys_tested: int = 1_000_000) -> Dict[str, Any]:
    """Test 1,000,000 random keys for collisions in round-key generation."""
    seen = set()
    collisions = 0
    for _ in range(keys_tested):
        key = random.getrandbits(64)
        rkeys = expand_key(key)
        signature = tuple(rkeys)
        if signature in seen:
            collisions += 1
        seen.add(signature)

    return {
        "keys_tested": keys_tested,
        "collisions": collisions,
        "collision_rate": collisions / keys_tested,
        "effective_key_space_percent": 100.0 * (1 - collisions / keys_tested),
    }


def shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy in bits per byte."""
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def chi_square_test(observed_counts: Dict[int, int]) -> Dict[str, Any]:
    """Run chi-square test on byte frequency distribution."""
    total = sum(observed_counts.values())
    if total == 0:
        return {"chi_square": 0.0, "degrees_of_freedom": 0, "p_value": 1.0}

    expected = total / 256.0
    chi_sq = sum(((obs - expected) ** 2) / expected for obs in observed_counts.values())
    df = 255
    # Approximate p-value using incomplete gamma
    from scipy.special import gammaincc
    p_value = float(gammaincc(df / 2.0, chi_sq / 2.0))

    return {
        "chi_square": chi_sq,
        "degrees_of_freedom": df,
        "p_value": p_value,
        "status": "PASS" if p_value > 0.01 else "FAIL",
    }


def generate_entropy_report() -> Dict[str, Any]:
    """Generate complete entropy analysis report."""
    random.seed(42)

    # Key collision test
    key_test = key_space_test(keys_tested=100_000)

    # Generate plaintext and ciphertext samples
    key = 0xA5A5A5A5A5A5A5A5
    rkeys = expand_key(key)
    plaintext_bytes = bytes(random.getrandbits(8) for _ in range(10_000))

    # Encrypt in 8-byte blocks
    ciphertext_bytes = bytearray()
    for i in range(0, len(plaintext_bytes), 8):
        block = int.from_bytes(plaintext_bytes[i:i + 8], "big")
        ct = lsa_encrypt(block, rkeys)
        ciphertext_bytes.extend(ct.to_bytes(8, "big"))

    pt_entropy = shannon_entropy(plaintext_bytes)
    ct_entropy = shannon_entropy(bytes(ciphertext_bytes))

    # Chi-square on ciphertext byte distribution
    counts = Counter(ciphertext_bytes)
    chi_result = chi_square_test(counts)

    return {
        "key_space": key_test,
        "plaintext_entropy_bits_per_byte": pt_entropy,
        "ciphertext_entropy_bits_per_byte": ct_entropy,
        "chi_square": chi_result,
    }
