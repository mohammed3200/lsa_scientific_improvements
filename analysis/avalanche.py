"""
Quantitative Avalanche Analysis for LSA.

Implements:
  - Strict Avalanche Criterion (SAC)
  - Bit Independence Criterion (BIC)
  - Number of Pixels Change Rate (NPCR)
  - Unified Average Changing Intensity (UACI)
"""

import math
import random
import numpy as np
from typing import Dict, Any

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lsa_project"))

from algorithms.lsa.key_expansion import expand_key
from algorithms.lsa.encrypt import lsa_encrypt


def strict_avalanche_criterion(
    plaintext: int,
    key: int,
    samples: int = 10_000,
) -> Dict[str, Any]:
    """
    Measure SAC: flipping one input bit should change ~50% of output bits.

    Returns average Hamming distance, standard deviation, and SAC score.
    """
    rkeys = expand_key(key)
    distances = []

    for _ in range(samples):
        bit_to_flip = 1 << random.randint(0, 63)
        ct1 = lsa_encrypt(plaintext, rkeys)
        ct2 = lsa_encrypt(plaintext ^ bit_to_flip, rkeys)
        diff = ct1 ^ ct2
        dist = bin(diff & 0xFFFFFFFFFFFFFFFF).count("1")
        distances.append(dist)

    avg_dist = np.mean(distances)
    std_dist = np.std(distances)
    ideal = 32.0
    sac_score = min(100.0, (avg_dist / ideal) * 100.0)

    return {
        "samples": samples,
        "avg_hamming_distance": float(avg_dist),
        "std_dev": float(std_dist),
        "ideal_distance": ideal,
        "sac_score_percent": float(sac_score),
    }


def bit_independence_criterion(
    plaintext: int,
    key: int,
    samples: int = 5_000,
) -> Dict[str, Any]:
    """
    Measure BIC: output bits should be pairwise independent.

    Computes correlation matrix of output bit flips.
    """
    rkeys = expand_key(key)
    flip_vectors = []

    for _ in range(samples):
        bit_to_flip = 1 << random.randint(0, 63)
        ct1 = lsa_encrypt(plaintext, rkeys)
        ct2 = lsa_encrypt(plaintext ^ bit_to_flip, rkeys)
        diff = ct1 ^ ct2
        flip_vector = np.array([(diff >> i) & 1 for i in range(64)], dtype=np.float64)
        flip_vectors.append(flip_vector)

    matrix = np.stack(flip_vectors)
    # Correlation matrix
    corr = np.corrcoef(matrix.T)
    # Exclude diagonal
    off_diag = corr[np.triu_indices_from(corr, k=1)]

    max_corr = float(np.max(np.abs(off_diag)))
    avg_corr = float(np.mean(np.abs(off_diag)))
    bic_score = max(0.0, 100.0 - max_corr * 100.0)

    return {
        "samples": samples,
        "max_correlation": max_corr,
        "avg_correlation": avg_corr,
        "bic_score_percent": float(bic_score),
    }


def npcr_test(plaintext1: int, plaintext2: int, key: int) -> Dict[str, Any]:
    """
    Number of Pixels Change Rate (adapted for 64-bit blocks).

    Measures percentage of differing bits between two ciphertexts
    from slightly different plaintexts.
    """
    rkeys = expand_key(key)
    ct1 = lsa_encrypt(plaintext1, rkeys)
    ct2 = lsa_encrypt(plaintext2, rkeys)
    diff = ct1 ^ ct2
    changed = bin(diff & 0xFFFFFFFFFFFFFFFF).count("1")
    npcr = (changed / 64.0) * 100.0

    return {
        "changed_bits": changed,
        "total_bits": 64,
        "npcr_percent": npcr,
        "ideal_percent": 100.0 * (1 - 1 / 64.0),  # ~98.44%
    }


def uaci_test(plaintext1: int, plaintext2: int, key: int) -> Dict[str, Any]:
    """
    Unified Average Changing Intensity (adapted for 64-bit blocks).

    Measures average intensity of bit changes between two ciphertexts.
    For binary data, UACI ≈ 50% when bits change randomly.
    """
    rkeys = expand_key(key)
    ct1 = lsa_encrypt(plaintext1, rkeys)
    ct2 = lsa_encrypt(plaintext2, rkeys)

    # For binary, UACI is equivalent to the ratio of changed bits
    diff = ct1 ^ ct2
    changed = bin(diff & 0xFFFFFFFFFFFFFFFF).count("1")
    uaci = (changed / 64.0) * 100.0

    return {
        "changed_bits": changed,
        "total_bits": 64,
        "uaci_percent": uaci,
        "ideal_percent": 50.0,
    }
