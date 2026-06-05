# Changelog

All notable changes to this project are documented in this file.

---

## [1.0.0-scientific] - Final Release

### Added
- `COMPARISON_REPORT.md` — Master audit comparing baseline vs improved.
- `GITHUB_RELEASE.md` — GitHub release notes.
- `visualization/comparison_dashboard.py` — Side-by-side graph generator.

---

## [1.0.0] - Formal Security Proof

### Added
- `proofs/formal_security.md` — IND-CPA proof sketch with reduction to PRESENT S-Box.
- `scripts/verify_proof_assumptions.py` — Validates S-Box branch number, active S-box count, LAT bias.

---

## [0.9.0] - Analytical PDR Model

### Added
- `models/pdr_model.py` — Markov-based exponential PDR model.
- `scripts/validate_pdr.py` — Fits λ and compares predicted vs simulated PDR.

---

## [0.8.0] - Side-Channel Resistance

### Added
- `analysis/side_channel.py` — Timing attack, DPA, and fault injection tests.
- `scripts/side_channel_report.py` — Generates side-channel resistance report.

---

## [0.7.0] - Entropy Analysis

### Added
- `analysis/entropy_analysis.py` — Key space collision test, Shannon entropy, chi-square.
- `scripts/entropy_report.py` — Generates entropy analysis report.

---

## [0.6.0] - ASCON Standard Comparison

### Added
- `analysis/ascon_comparison.py` — Feature comparison with NIST ASCON-128.
- `scripts/ascon_report.py` — Security margin and upgrade recommendations.

---

## [0.5.0] - Analytical Energy Model

### Added
- `models/energy_model.py` — First-order radio model with TX/RX/encryption energy.
- `scripts/validate_energy.py` — Validates analytical model against simulation.

---

## [0.4.0] - Avalanche Analysis

### Added
- `analysis/avalanche.py` — SAC, BIC, NPCR, UACI measurements.
- `scripts/avalanche_report.py` — Generates avalanche analysis report.

---

## [0.3.0] - NIST Statistical Tests

### Added
- `tests/nist_suite.py` — 15 NIST SP 800-22 randomness tests.
- `tests/run_nist_tests.py` — Test runner with JSON/Markdown output.

---

## [0.2.0] - Theoretical Security Analysis

### Added
- `analysis/security_theory.py` — Brute-force, differential, linear cryptanalysis.
- `scripts/security_report.py` — Generates theoretical security report.

---

## [0.1.0] - Complexity Analysis

### Added
- `analysis/complexity.py` — Operation counts and asymptotic complexity.
- `scripts/generate_complexity_table.py` — Comparison table generator.

---

## [0.0.0] - Baseline

### Added
- Original LSA implementation (SIT key expansion + SPINS key management).
- SPN and Feistel baseline algorithms for comparison.
- Four simulation metrics: Key Expansion Time, Security Level, Energy Consumption, Packet Delivery Ratio.
- Matplotlib visualization for publication-quality graphs.
- Network simulation with IEEE 802.11s-inspired model.

### Notes
- This is the starting point before scientific improvements.
- All 10 improvements are tracked in `BASELINE.md` as `[PENDING]`.
