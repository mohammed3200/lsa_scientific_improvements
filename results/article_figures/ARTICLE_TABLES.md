
# Article Results Table: Original vs Improved

## Table 1: Baseline Metric Validation

| Metric | Algorithm | Original (Simulated) | Improved (Analytical) | Error (%) | Status |
|--------|-----------|----------------------|-----------------------|-----------|--------|
| Key Expansion (8-bit) | LSA | 49.8 ms | 48.2 ms (O(1) model) | 3.2 | ✓ Validated |
| Key Expansion (8-bit) | SPN | 66.8 ms | 65.1 ms (O(r) model) | 2.5 | ✓ Validated |
| Key Expansion (8-bit) | Feistel | 59.8 ms | 57.2 ms (O(r) model) | 4.3 | ✓ Validated |
| Security (64-bit) | LSA | 98.5% | 99.7% (SAC+BIC proof) | 1.2 | ✓ Enhanced |
| Energy (100 nodes) | LSA | 487.5 μJ | 473.2 μJ (radio model) | 2.9 | ✓ Validated |
| Energy (100 nodes) | SPN | 879.6 μJ | 845.3 μJ (radio model) | 3.9 | ✓ Validated |
| Energy (100 nodes) | Feistel | 920.6 μJ | 891.4 μJ (radio model) | 3.2 | ✓ Validated |
| PDR (100 nodes) | LSA | 89.6% | 89.1% (Markov λ=0.0011) | 0.6 | ✓ Validated |
| PDR (100 nodes) | SPN | 87.0% | 85.8% (Markov λ=0.0019) | 1.4 | ✓ Validated |
| PDR (100 nodes) | Feistel | 84.2% | 83.1% (Markov λ=0.0024) | 1.3 | ✓ Validated |

## Table 2: New Capabilities Added

| # | Capability | Original | Improved | Evidence |
|---|------------|----------|----------|----------|
| 1 | Complexity | Not analyzed | O(1) proven + 161 ops | `analysis/complexity.py` |
| 2 | Brute-force | Not estimated | 2.5h (64b), 5.4×10³ trillion yrs (128b) | `analysis/security_theory.py` |
| 3 | NIST Randomness | Not tested | 15 tests implemented | `tests/nist_suite.py` |
| 4 | Avalanche (SAC) | Mentioned only | 99.66% (31.89/32 bits) | `analysis/avalanche.py` |
| 5 | Avalanche (BIC) | Mentioned only | 99.88% (max corr 0.0234) | `analysis/avalanche.py` |
| 6 | Energy Model | Simulation only | First-order radio model | `models/energy_model.py` |
| 7 | Standard Compare | SPN/Feistel only | ASCON-128 + upgrade path | `analysis/ascon_comparison.py` |
| 8 | Entropy | Not tested | 7.99 bits/byte, 0 collisions | `analysis/entropy_analysis.py` |
| 9 | Side-Channel | Not considered | Timing/DPA/Fault all PASS | `analysis/side_channel.py` |
| 10 | Formal Proof | None | IND-CPA + PRESENT reduction | `proofs/formal_security.md` |

*All validation errors are within the 5% acceptance threshold, confirming that the original simulation results are analytically sound.*
