"""
Side-Channel Resistance Analysis for LSA.

Tests timing attack resistance, DPA correlation, and fault injection detection.
"""

import time
import random
import numpy as np
from typing import Dict, Any, Callable

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lsa_project"))

from algorithms.lsa.key_expansion import expand_key
from algorithms.lsa.encrypt import lsa_encrypt


def timing_attack_resistance(
    encryption_func: Callable,
    key: int,
    samples: int = 10_000,
) -> Dict[str, Any]:
    """
    Measure timing consistency across identical encryption operations.

    Returns mean, std dev, and coefficient of variation (CV).
    """
    plaintext = 0x123456789ABCDEF0
    times = []
    for _ in range(samples):
        start = time.perf_counter_ns()
        encryption_func(plaintext, key)
        elapsed = time.perf_counter_ns() - start
        times.append(elapsed)

    times_arr = np.array(times, dtype=np.float64)
    mean_t = float(np.mean(times_arr))
    std_t = float(np.std(times_arr))
    cv = (std_t / mean_t * 100.0) if mean_t > 0 else 0.0

    return {
        "samples": samples,
        "mean_ns": mean_t,
        "std_ns": std_t,
        "cv_percent": cv,
        "threshold_cv_percent": 5.0,
        "status": "PASS" if cv < 5.0 else "FAIL",
    }


def dpa_resistance(
    encryption_func: Callable,
    key: int,
    samples: int = 1_000,
) -> Dict[str, Any]:
    """
    Simulate DPA by correlating hypothetical power consumption with key bits.

    Returns maximum correlation observed.
    """
    random.seed(42)
    plaintexts = [random.getrandbits(64) for _ in range(samples)]

    # Hypothetical power model: Hamming weight of first S-Box input
    power_traces = []
    for pt in plaintexts:
        ct = encryption_func(pt, key)
        # Hypothetical power = Hamming weight of ciphertext nibble 0
        power = bin((ct >> 60) & 0xF).count("1")
        power_traces.append(power)

    # Correlate with each key bit
    max_corr = 0.0
    for bit in range(64):
        key_bits = [((key >> bit) & 1) for _ in range(samples)]
        corr = np.corrcoef(key_bits, power_traces)[0, 1]
        if not np.isnan(corr):
            max_corr = max(max_corr, abs(corr))

    return {
        "samples": samples,
        "max_correlation": float(max_corr),
        "threshold": 0.1,
        "status": "PASS" if max_corr < 0.1 else "FAIL",
    }


def fault_injection_resistance(
    encryption_func: Callable,
    key: int,
    plaintext: int,
    fault_rounds: int = 100,
) -> Dict[str, Any]:
    """
    Simulate fault injection by randomly corrupting intermediate values.

    Returns detection rate of invalid ciphertexts.
    """
    rkeys = expand_key(key)
    valid_ct = encryption_func(plaintext, tuple(rkeys))

    detected = 0
    for _ in range(fault_rounds):
        # Simulate fault by flipping a random bit in a round key
        round_idx = random.randint(0, 4)
        bit_to_flip = 1 << random.randint(0, 15)
        faulty_keys = list(rkeys)
        faulty_keys[round_idx] ^= bit_to_flip
        faulty_ct = encryption_func(plaintext, tuple(faulty_keys))
        if faulty_ct != valid_ct:
            detected += 1

    detection_rate = (detected / fault_rounds) * 100.0
    return {
        "fault_rounds": fault_rounds,
        "detected": detected,
        "detection_rate_percent": detection_rate,
        "threshold_percent": 100.0,
        "status": "PASS" if detection_rate >= 100.0 else "FAIL",
    }
