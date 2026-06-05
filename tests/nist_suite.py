"""
NIST SP 800-22 Statistical Test Suite for Ciphertext Randomness.

Implements 15 standard randomness tests. Each returns a p-value.
Pass if p-value > 0.01.
"""

import math
import random
import numpy as np
from scipy.special import gammaincc, erfc
from typing import Dict, List, Tuple, Any

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lsa_project"))

from algorithms.lsa.key_expansion import expand_key
from algorithms.lsa.encrypt import lsa_encrypt


# ---------------------------------------------------------------------------
# Helper: generate bit sequence from LSA
# ---------------------------------------------------------------------------

def generate_lsa_bit_sequence(num_bits: int = 1_000_000, seed: int = 42) -> np.ndarray:
    """Generate a sequence of ciphertext bits from LSA for testing."""
    np.random.seed(seed)
    random.seed(seed)
    bits = []
    key = 0xA5A5A5A5A5A5A5A5
    rkeys = expand_key(key)

    blocks_needed = (num_bits + 63) // 64
    for i in range(blocks_needed):
        plaintext = random.getrandbits(64)
        ciphertext = lsa_encrypt(plaintext, rkeys)
        block_bits = [(ciphertext >> j) & 1 for j in range(64)]
        bits.extend(block_bits)

    return np.array(bits[:num_bits], dtype=np.int32)


# ---------------------------------------------------------------------------
# Test 1: Frequency (Monobit) Test
# ---------------------------------------------------------------------------

def frequency_monobit_test(bits: np.ndarray) -> float:
    n = len(bits)
    s = 2 * bits.sum() - n
    s_obs = abs(s) / math.sqrt(n)
    p_value = erfc(s_obs / math.sqrt(2))
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 2: Frequency within a Block Test
# ---------------------------------------------------------------------------

def frequency_block_test(bits: np.ndarray, block_size: int = 100) -> float:
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return 0.0

    chi_sq = 0.0
    for i in range(num_blocks):
        block = bits[i * block_size:(i + 1) * block_size]
        pi = block.sum() / block_size
        chi_sq += 4 * block_size * (pi - 0.5) ** 2

    p_value = gammaincc(num_blocks / 2.0, chi_sq / 2.0)
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 3: Runs Test
# ---------------------------------------------------------------------------

def runs_test(bits: np.ndarray) -> float:
    n = len(bits)
    pi = bits.sum() / n
    if abs(pi - 0.5) >= 2.0 / math.sqrt(n):
        return 0.0

    v = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            v += 1

    num = abs(v - 2 * n * pi * (1 - pi))
    den = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    p_value = erfc(num / den)
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 4: Longest Run of Ones in a Block Test
# ---------------------------------------------------------------------------

def longest_run_ones_test(bits: np.ndarray) -> float:
    n = len(bits)
    block_size = 8 if n < 128 else (128 if n < 6272 else (512 if n < 750000 else 1000))
    num_blocks = n // block_size
    if num_blocks < 1:
        return 0.0

    # Expected frequencies for block_size=128 (simplified)
    if block_size == 128:
        classes = [1, 2, 3, 4, 5, 6]  # longest run categories
        probs = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
        max_run_threshold = 5
    else:
        # Simplified fallback
        classes = [1, 2, 3, 4]
        probs = [0.25, 0.25, 0.25, 0.25]
        max_run_threshold = 3

    counts = [0] * len(classes)
    for i in range(num_blocks):
        block = bits[i * block_size:(i + 1) * block_size]
        max_run = 0
        current = 0
        for b in block:
            if b == 1:
                current += 1
                max_run = max(max_run, current)
            else:
                current = 0
        idx = min(max_run, len(classes) - 1)
        counts[idx] += 1

    chi_sq = 0.0
    for i in range(len(classes)):
        expected = num_blocks * probs[i]
        if expected > 0:
            chi_sq += (counts[i] - expected) ** 2 / expected

    p_value = gammaincc((len(classes) - 1) / 2.0, chi_sq / 2.0)
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 5: Binary Matrix Rank Test
# ---------------------------------------------------------------------------

def binary_matrix_rank_test(bits: np.ndarray, matrix_size: int = 32) -> float:
    n = len(bits)
    num_matrices = n // (matrix_size * matrix_size)
    if num_matrices < 1:
        return 0.0

    ranks = []
    for m in range(num_matrices):
        matrix_bits = bits[m * matrix_size * matrix_size:(m + 1) * matrix_size * matrix_size]
        matrix = matrix_bits.reshape((matrix_size, matrix_size))
        rank = np.linalg.matrix_rank(matrix)
        ranks.append(rank)

    # Expected probabilities for 32x32 matrices
    p_full = 0.2888
    p_full_minus_1 = 0.5776
    p_other = 1 - p_full - p_full_minus_1

    f_full = sum(1 for r in ranks if r == matrix_size)
    f_full_minus_1 = sum(1 for r in ranks if r == matrix_size - 1)
    f_other = len(ranks) - f_full - f_full_minus_1

    chi_sq = (
        (f_full - num_matrices * p_full) ** 2 / (num_matrices * p_full)
        + (f_full_minus_1 - num_matrices * p_full_minus_1) ** 2 / (num_matrices * p_full_minus_1)
        + (f_other - num_matrices * p_other) ** 2 / (num_matrices * p_other)
    )

    p_value = math.exp(-chi_sq / 2.0)
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 6: Discrete Fourier Transform (Spectral) Test
# ---------------------------------------------------------------------------

def dft_test(bits: np.ndarray) -> float:
    n = len(bits)
    # Convert to -1, +1
    x = 2 * bits.astype(np.float64) - 1
    xf = np.fft.fft(x)
    magnitudes = np.abs(xf[:n // 2])

    threshold = math.sqrt(2.995732274 * n)
    n0 = 0.95 * n / 2.0
    n1 = sum(1 for m in magnitudes if m < threshold)

    d = (n1 - n0) / math.sqrt(n * 0.95 * 0.05 / 4.0)
    p_value = erfc(abs(d) / math.sqrt(2))
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 7: Non-overlapping Template Matching Test
# ---------------------------------------------------------------------------

def non_overlapping_template_test(bits: np.ndarray, template: List[int] = None, block_size: int = 1032) -> float:
    n = len(bits)
    m = 9  # template length
    if template is None:
        template = [1, 0, 1, 0, 0, 1, 1, 0, 1]
    num_blocks = n // block_size
    if num_blocks < 1:
        return 0.0

    mu = (block_size - m + 1) / (2 ** m)
    sigma = block_size * ((1 / (2 ** m)) - ((2 * m - 1) / (2 ** (2 * m))))

    chi_sq = 0.0
    for b in range(num_blocks):
        block = bits[b * block_size:(b + 1) * block_size]
        count = 0
        i = 0
        while i <= block_size - m:
            if np.array_equal(block[i:i + m], template):
                count += 1
                i += m
            else:
                i += 1
        chi_sq += ((count - mu) ** 2) / sigma

    p_value = gammaincc(num_blocks / 2.0, chi_sq / 2.0)
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 8: Overlapping Template Matching Test
# ---------------------------------------------------------------------------

def overlapping_template_test(bits: np.ndarray, block_size: int = 1032) -> float:
    n = len(bits)
    m = 9
    num_blocks = n // block_size
    if num_blocks < 1:
        return 0.0

    template = np.ones(m, dtype=np.int32)
    lambda_ = (block_size - m + 1) / (2 ** m)
    eta = lambda_ / 2.0

    counts = [0, 0, 0, 0, 0, 0]
    for b in range(num_blocks):
        block = bits[b * block_size:(b + 1) * block_size]
        count = 0
        for i in range(block_size - m + 1):
            if np.array_equal(block[i:i + m], template):
                count += 1
        idx = min(count, 5)
        counts[idx] += 1

    # Expected probabilities (Poisson approx)
    probs = [
        math.exp(-eta),
        eta * math.exp(-eta),
        (eta ** 2 / 2) * math.exp(-eta),
        (eta ** 3 / 6) * math.exp(-eta),
        (eta ** 4 / 24) * math.exp(-eta),
        1 - sum([(eta ** i / math.factorial(i)) * math.exp(-eta) for i in range(5)]),
    ]

    chi_sq = 0.0
    for i in range(6):
        expected = num_blocks * probs[i]
        if expected > 0:
            chi_sq += (counts[i] - expected) ** 2 / expected

    p_value = gammaincc(5.0 / 2.0, chi_sq / 2.0)
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 9: Maurer's Universal Statistical Test
# ---------------------------------------------------------------------------

def maurers_universal_test(bits: np.ndarray, L: int = 6) -> float:
    n = len(bits)
    Q = 10 * (2 ** L)
    K = n // L - Q
    if K < 1:
        return 0.0

    table = {}
    for i in range(Q):
        block = tuple(bits[i * L:(i + 1) * L])
        table[block] = i

    sum_log = 0.0
    for i in range(Q, Q + K):
        block = tuple(bits[i * L:(i + 1) * L])
        if block in table:
            dist = i - table[block]
            sum_log += math.log2(dist)
        table[block] = i

    fn = sum_log / K
    c = 0.7 - 0.8 / L + (4 + 32.0 / L) * (K ** (-3.0 / L)) / 15
    sigma = c * math.sqrt((0.5 ** L) * ((1 - (0.5 ** L)) / K))
    expected = 0.5 * L + (math.log(1 - (0.5 ** L)) / math.log(2))

    p_value = erfc(abs(fn - expected) / (math.sqrt(2) * sigma))
    return float(p_value)


# ---------------------------------------------------------------------------
# Test 10: Linear Complexity Test
# ---------------------------------------------------------------------------

def linear_complexity_test(bits: np.ndarray, block_size: int = 500) -> float:
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks < 1:
        return 0.0

    mu = block_size / 2.0 + (9 + (-1) ** (block_size + 1)) / 36.0 - (block_size / 3.0 + 2.0 / 9.0) / (2 ** block_size)
    t_values = []
    for b in range(num_blocks):
        block = bits[b * block_size:(b + 1) * block_size]
        lc = _berlekamp_massey(block)
        t = ((-1) ** block_size) * (lc - mu) + 2.0 / 9.0
        t_values.append(t)

    chi_sq = sum(t ** 2 for t in t_values)
    p_value = gammaincc(num_blocks / 2.0, chi_sq / 2.0)
    return float(p_value)


def _berlekamp_massey(bits: np.ndarray) -> int:
    """Compute linear complexity of a binary sequence."""
    n = len(bits)
    c = np.zeros(n, dtype=np.int32)
    b = np.zeros(n, dtype=np.int32)
    c[0] = 1
    b[0] = 1
    l = 0
    m = -1

    for i in range(n):
        d = bits[i]
        for j in range(1, l + 1):
            d ^= c[j] & bits[i - j]
        if d == 1:
            t = c.copy()
            for j in range(n - i + m):
                c[i - m + j] ^= b[j]
            if 2 * l <= i:
                l = i + 1 - l
                m = i
                b = t
    return l


# ---------------------------------------------------------------------------
# Test 11: Serial Test
# ---------------------------------------------------------------------------

def serial_test(bits: np.ndarray, m: int = 16) -> Tuple[float, float]:
    n = len(bits)
    p1 = _serial_psi(bits, n, m)
    p2 = _serial_psi(bits, n, m - 1)
    p3 = _serial_psi(bits, n, m - 2)

    d1 = p1 - p2
    d2 = p1 - 2 * p2 + p3

    p1_val = gammaincc(2 ** (m - 2), d1 / 2.0)
    p2_val = gammaincc(2 ** (m - 3), d2 / 2.0)
    return float(p1_val), float(p2_val)


def _serial_psi(bits: np.ndarray, n: int, m: int) -> float:
    if m == 0:
        return 0.0
    counts = {}
    for i in range(n):
        block = tuple(bits[i:i + m])
        if len(block) == m:
            counts[block] = counts.get(block, 0) + 1
    total = sum(v ** 2 for v in counts.values())
    return (2 ** m) * total / n - n


# ---------------------------------------------------------------------------
# Test 12: Approximate Entropy Test
# ---------------------------------------------------------------------------

def approximate_entropy_test(bits: np.ndarray, m: int = 10) -> float:
    n = len(bits)
    phi_m = _approx_entropy_phi(bits, n, m)
    phi_m1 = _approx_entropy_phi(bits, n, m + 1)

    chi_sq = 2 * n * (math.log(2) - (phi_m - phi_m1))
    p_value = gammaincc(2 ** m, chi_sq / 2.0)
    return float(p_value)


def _approx_entropy_phi(bits: np.ndarray, n: int, m: int) -> float:
    if m == 0:
        return 0.0
    counts = {}
    for i in range(n):
        block = tuple(bits[i:i + m])
        if len(block) == m:
            counts[block] = counts.get(block, 0) + 1
    total = 0.0
    for v in counts.values():
        p = v / n
        total += p * math.log(p)
    return total


# ---------------------------------------------------------------------------
# Test 13: Cumulative Sums (Cusum) Test
# ---------------------------------------------------------------------------

def cumulative_sums_test(bits: np.ndarray) -> Tuple[float, float]:
    n = len(bits)
    x = 2 * bits.astype(np.int32) - 1

    # Forward
    s = np.cumsum(x)
    z_forward = max(abs(s))

    # Backward
    s_rev = np.cumsum(x[::-1])
    z_backward = max(abs(s_rev))

    p_forward = _cusum_pvalue(z_forward, n)
    p_backward = _cusum_pvalue(z_backward, n)
    return float(p_forward), float(p_backward)


def _cusum_pvalue(z: int, n: int) -> float:
    """Simplified CUSUM p-value approximation clamped to [0, 1]."""
    k_start = max(-10, int((-n / z + 1) / 4))
    k_end = min(10, int((n / z - 1) / 4))
    p = 0.0
    for k in range(k_start, k_end + 1):
        c1 = (4 * k + 1) * z / math.sqrt(n)
        c2 = (4 * k - 1) * z / math.sqrt(n)
        p += erfc(c1 / math.sqrt(2)) - erfc(c2 / math.sqrt(2))
    return max(0.0, min(1.0, p))


# ---------------------------------------------------------------------------
# Test 14: Random Excursions Test
# ---------------------------------------------------------------------------

def random_excursions_test(bits: np.ndarray) -> List[Tuple[int, float]]:
    n = len(bits)
    x = 2 * bits.astype(np.int32) - 1
    s = np.cumsum(x)
    s = np.concatenate(([0], s, [0]))

    # Find cycles
    cycles = []
    start = 0
    for i in range(1, len(s)):
        if s[i] == 0:
            cycles.append(s[start:i + 1])
            start = i

    if len(cycles) < 1:
        return []

    states = [-4, -3, -2, -1, 1, 2, 3, 4]
    results = []
    for state in states:
        counts = [0, 0, 0, 0, 0, 0]
        for cycle in cycles:
            visits = sum(1 for v in cycle if v == state)
            idx = min(visits, 5)
            counts[idx] += 1

        # Expected probabilities for random excursions
        probs = [0.5, 0.25, 0.125, 0.0625, 0.03125, 0.03125]
        chi_sq = 0.0
        for i in range(6):
            expected = len(cycles) * probs[i]
            if expected > 0:
                chi_sq += (counts[i] - expected) ** 2 / expected

        p_value = gammaincc(5.0 / 2.0, chi_sq / 2.0)
        results.append((state, float(p_value)))

    return results


# ---------------------------------------------------------------------------
# Test 15: Random Excursions Variant Test
# ---------------------------------------------------------------------------

def random_excursions_variant_test(bits: np.ndarray) -> List[Tuple[int, float]]:
    n = len(bits)
    x = 2 * bits.astype(np.int32) - 1
    s = np.cumsum(x)
    s = np.concatenate(([0], s, [0]))

    cycles = []
    start = 0
    for i in range(1, len(s)):
        if s[i] == 0:
            cycles.append(s[start:i + 1])
            start = i

    if len(cycles) < 1:
        return []

    states = list(range(-9, 10))
    states.remove(0)
    results = []
    for state in states:
        count = sum(sum(1 for v in cycle if v == state) for cycle in cycles)
        p_value = erfc(abs(count - len(cycles)) / math.sqrt(2 * len(cycles) * (4 * abs(state) - 2)))
        results.append((state, float(p_value)))

    return results


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def run_all_tests(bits: np.ndarray) -> Dict[str, Dict[str, Any]]:
    """Run all 15 NIST tests and return structured results."""
    results = {}

    # 1. Frequency
    p = frequency_monobit_test(bits)
    results["Frequency (Monobit)"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 2. Frequency within Block
    p = frequency_block_test(bits)
    results["Frequency within Block"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 3. Runs
    p = runs_test(bits)
    results["Runs"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 4. Longest Run of Ones
    p = longest_run_ones_test(bits)
    results["Longest Run of Ones"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 5. Binary Matrix Rank
    p = binary_matrix_rank_test(bits)
    results["Binary Matrix Rank"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 6. DFT
    p = dft_test(bits)
    results["Discrete Fourier Transform"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 7. Non-overlapping Template
    p = non_overlapping_template_test(bits)
    results["Non-overlapping Template"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 8. Overlapping Template
    p = overlapping_template_test(bits)
    results["Overlapping Template"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 9. Maurer's Universal
    p = maurers_universal_test(bits)
    results["Maurer's Universal"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 10. Linear Complexity
    p = linear_complexity_test(bits)
    results["Linear Complexity"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 11. Serial
    p1, p2 = serial_test(bits)
    results["Serial (1)"] = {"p_value": p1, "status": "PASS" if p1 > 0.01 else "FAIL"}
    results["Serial (2)"] = {"p_value": p2, "status": "PASS" if p2 > 0.01 else "FAIL"}

    # 12. Approximate Entropy
    p = approximate_entropy_test(bits)
    results["Approximate Entropy"] = {"p_value": p, "status": "PASS" if p > 0.01 else "FAIL"}

    # 13. Cumulative Sums
    pf, pb = cumulative_sums_test(bits)
    results["Cumulative Sums (Forward)"] = {"p_value": pf, "status": "PASS" if pf > 0.01 else "FAIL"}
    results["Cumulative Sums (Backward)"] = {"p_value": pb, "status": "PASS" if pb > 0.01 else "FAIL"}

    # 14. Random Excursions
    re_results = random_excursions_test(bits)
    all_pass = all(p > 0.01 for _, p in re_results)
    results["Random Excursions"] = {
        "p_values": {f"state_{s}": p for s, p in re_results},
        "status": "PASS" if all_pass else "FAIL",
    }

    # 15. Random Excursions Variant
    rev_results = random_excursions_variant_test(bits)
    all_pass = all(p > 0.01 for _, p in rev_results)
    results["Random Excursions Variant"] = {
        "p_values": {f"state_{s}": p for s, p in rev_results},
        "status": "PASS" if all_pass else "FAIL",
    }

    return results
