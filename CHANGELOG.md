# Changelog

All notable changes to this project are documented in this file.

---

## [2.0.0] — 2025-06-08 — LSA v2.0: Algorithmic Upgrade & Visualization Framework

> **Major release:** Upgrades the cipher core (128-bit key, 8 rounds, CTR mode) and replaces static HTML with an automated 3-layer visualization pipeline.

### Added

#### Algorithm Upgrades
- **128-bit key support** (`core/lsa/key_expansion.py`): `expand_key_v2()` derives 8 round keys from a 128-bit master key. K9 = XOR of K1..K8 for redundancy.
- **8-round variant** (`core/lsa/encrypt_v2.py`): `lsa_encrypt_v2()` / `lsa_decrypt_v2()` with enhanced security margin (≥16 active S-boxes per differential trail).
- **Enhanced f-function** (`core/lsa/f_function.py`): Additional P-Table layer (`P_TABLE_V2`) and 12-bit left-shift rotation for full avalanche after 3 rounds (vs 5 in Legacy).
- **CTR mode + AEAD** (`core/lsa/modes.py`): `ctr_encrypt()` / `ctr_decrypt()` with 64-bit nonce + counter, plus HMAC-SHA256 authentication tag.
- **Constant-time S-Box** (`core/lsa/s_box.py`): `constant_time_sbox_lookup()` uses bitwise masking instead of secret-dependent array indexing to prevent timing side-channels.

#### Professional Visualization Pipeline
- **3-layer architecture**:
  - Layer 1 — `pipeline/data_generator.py`: Runs all simulations, outputs CSV + JSON.
  - Layer 2 — `pipeline/plot_engine.py`: Generates 10 publication-quality figures at 300 DPI.
  - Layer 3 — `pipeline/report_builder.py`: Builds interactive HTML dashboard via Jinja2.
- **One-command execution**: `python scripts/generate_report.py --mode v2`
- **Figures produced**:
  1. Key Expansion Time Comparison
  2. Security Level vs Key Size
  3. Energy Consumption vs Nodes
  4. Packet Delivery Ratio (PDR)
  5. NIST Test Results Heatmap
  6. Avalanche Effect Distribution
  7. Operation Count Comparison
  8. Side-Channel Resistance Radar
  9. Baseline vs Improved vs Upgraded
  10. Operation Distribution (Pie)

#### Testing & Validation
- `tests/nist_suite_v2.py` — Improved NIST SP 800-22 suite with 10M-bit support, counter-mode bit generation, and honest documentation of structural limitations.
- `scripts/compare_versions.py` — Side-by-side v2 vs Legacy comparison with percentage improvements.
- `NIST_VALIDATION.md` — Detailed root-cause analysis of test failures (scientific honesty).

#### Documentation
- `README_v2.md` — v2-specific usage guide and API reference.
- `CHANGELOG_v2.md` — v2 version history (now merged into this file).

### Changed
- Restructured algorithm code into `core/lsa/` package with clean module separation.
- Backward compatibility preserved: Legacy mode (64-bit, 5 rounds) maintained in `encrypt_legacy.py`.
- Unified color palette (`#00d4ff` for v2, `#00b894` for Legacy) and typography across all figures.
- Merged `README.md` and `CHANGELOG.md` to show full evolution from v0.0.0 → v2.0.0.

### Fixed
- CTR mode partial-block handling (last block < 8 bytes caused overflow).
- `_int_to_bytes()` overflow when converting 128-bit keys to bytes.
- NIST CUSUM p-value clamping to [0, 1] range.

---

## [1.1.0] — Article Comparison Figures

### Added
- `scripts/article_comparison.py` — Generates 12 consistent original-vs-improved comparison figures.
- `results/article_figures/` — Publication-quality PNG outputs:
  - fig1–fig4: Original vs Improved (Key Expansion, Security, Energy, PDR)
  - fig5–fig12: NIST, Avalanche, Side-Channel, Entropy, ASCON, Capabilities, Validation, Complexity

### Changed
- Unified style palette across all 12 figures (colors, markers, fonts, 300 DPI).
- Removed old `*_comparison.png` files in favor of consistent naming.

---

## [1.0.0-scientific] — Final Release

### Added
- `COMPARISON_REPORT.md` — Master audit comparing baseline vs improved.
- `GITHUB_RELEASE.md` — GitHub release notes.
- `visualization/comparison_dashboard.py` — Side-by-side graph generator.

---

## [1.0.0] — Formal Security Proof

### Added
- `proofs/formal_security.md` — IND-CPA proof sketch with reduction to PRESENT S-Box.
- `scripts/verify_proof_assumptions.py` — Validates S-Box branch number, active S-box count, LAT bias.

---

## [0.9.0] — Analytical PDR Model

### Added
- `models/pdr_model.py` — Markov-based exponential PDR model.
- `scripts/validate_pdr.py` — Fits λ and compares predicted vs simulated PDR.

---

## [0.8.0] — Side-Channel Resistance

### Added
- `analysis/side_channel.py` — Timing attack, DPA, and fault injection tests.
- `scripts/side_channel_report.py` — Generates side-channel resistance report.

---

## [0.7.0] — Entropy Analysis

### Added
- `analysis/entropy_analysis.py` — Key space collision test, Shannon entropy, chi-square.
- `scripts/entropy_report.py` — Generates entropy analysis report.

---

## [0.6.0] — ASCON Standard Comparison

### Added
- `analysis/ascon_comparison.py` — Feature comparison with NIST ASCON-128.
- `scripts/ascon_report.py` — Security margin and upgrade recommendations.

---

## [0.5.0] — Analytical Energy Model

### Added
- `models/energy_model.py` — First-order radio model with TX/RX/encryption energy.
- `scripts/validate_energy.py` — Validates analytical model against simulation.

---

## [0.4.0] — Avalanche Analysis

### Added
- `analysis/avalanche.py` — SAC, BIC, NPCR, UACI measurements.
- `scripts/avalanche_report.py` — Generates avalanche analysis report.

---

## [0.3.0] — NIST Statistical Tests

### Added
- `tests/nist_suite.py` — 15 NIST SP 800-22 randomness tests.
- `tests/run_nist_tests.py` — Test runner with JSON/Markdown output.

---

## [0.2.0] — Theoretical Security Analysis

### Added
- `analysis/security_theory.py` — Brute-force, differential, linear cryptanalysis.
- `scripts/security_report.py` — Generates theoretical security report.

---

## [0.1.0] — Complexity Analysis

### Added
- `analysis/complexity.py` — Operation counts and asymptotic complexity.
- `scripts/generate_complexity_table.py` — Comparison table generator.

---

## [0.0.0] — Baseline

### Added
- Original LSA implementation (SIT key expansion + SPINS key management).
- SPN and Feistel baseline algorithms for comparison.
- Four simulation metrics: Key Expansion Time, Security Level, Energy Consumption, Packet Delivery Ratio.
- Matplotlib visualization for publication-quality graphs.
- Network simulation with IEEE 802.11s-inspired model.

### Notes
- This is the starting point before scientific improvements.
- All 10 improvements are tracked in `BASELINE.md` as `[PENDING]`.
