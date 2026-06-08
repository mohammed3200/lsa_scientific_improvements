# LSA Scientific Improvements

**Project:** Lightweight Security Algorithm (LSA) — Research-Grade Hardening  
**Reference:** Mahlake et al., *Journal of Communications*, Vol. 18, No. 1, 2023  
**License:** MIT

---

## Overview

This repository contains a scientifically hardened implementation of the LSA (Lightweight Security Algorithm) hybrid cipher for Wireless Sensor Networks (WSNs) in IoT. It extends the original four-metric simulation with **two major releases**:

| Release | Focus | Key Achievement |
|---------|-------|-----------------|
| **v1.0.x** | 10 scientific improvements on the original cipher | Formal proofs, NIST validation, ASCON comparison |
| **v2.0.0** | Algorithmic upgrades + professional visualization pipeline | 128-bit key, 8 rounds, CTR mode, auto-generated dashboard |

---

## Baseline Description (Original Paper)

The original LSA implementation provides:
- **Algorithm:** LSA hybrid cipher (SIT key expansion + SPINS key management)
- **Parameters:** 64-bit block, 64-bit key, 5 rounds, 4×4 S-Box
- **Baselines:** SPN and Feistel Network for comparative evaluation
- **Metrics:** Four publication-quality graphs (key expansion, security, energy, PDR)
- **Simulation:** 100 nodes, 400×400 m², IEEE 802.11s model, 10-run averaging

---

## What's New in v2.0.0

### 🔐 Algorithmic Upgrades

| Feature | v1.0 (Legacy) | **v2.0** | Impact |
|---------|---------------|----------|--------|
| Key Size | 64-bit | **128-bit** | 2^64 → 2^128 key space |
| Rounds | 5 | **8** | ≥16 active S-boxes per trail |
| f-function | 4 layers (AND→Shift→S-Box→OR) | **5 layers + P-Table** | Full avalanche after 3 rounds |
| S-Box Access | Variable-time array indexing | **Constant-time masking** | Timing side-channel resistant |
| Mode | ECB-only | **CTR + AEAD (HMAC-SHA256)** | Practical IoT deployment |

### 📊 Professional Visualization Pipeline

Replaced static HTML with an **automated, data-driven 3-layer pipeline**:

```
Layer 1: Data Generator (Python)     → CSV + JSON datasets
Layer 2: Plot Engine (Matplotlib)    → 10 PNG figures @ 300 DPI
Layer 3: Report Builder (Jinja2)     → Interactive HTML dashboard
```

Run everything with one command:
```bash
python scripts/generate_report.py --mode v2
```

### 📁 New Directory Structure

```
lsa_scientific_improvements/
├── README.md                          # This file (merged v1 + v2)
├── CHANGELOG.md                       # Full version history (v0.0.0 → v2.0.0)
├── NIST_VALIDATION.md                 # Honest NIST test results with root cause analysis
├── requirements.txt                   # Python dependencies
├── lsa_project/                       # Original v1.0 implementation
│   ├── main.py
│   ├── config.py
│   ├── algorithms/lsa/                # Legacy encrypt.py, key_expansion.py, etc.
│   ├── network/
│   ├── metrics/
│   └── visualization/
├── core/                              # NEW: v2.0 algorithm package
│   └── lsa/
│       ├── constants.py               # S-Box, P_TABLE_V2, mode config
│       ├── s_box.py                   # Constant-time lookup
│       ├── f_function.py              # Legacy + enhanced f-function
│       ├── key_expansion.py           # 64-bit AND 128-bit key schedule
│       ├── encrypt_legacy.py          # Original 5-round LSA
│       ├── encrypt_v2.py              # 8-round LSA v2
│       └── modes.py                   # CTR mode + AEAD tag
├── analysis/                          # v1.0: complexity, security, avalanche
├── tests/
│   ├── nist_suite.py                  # v1.0: original NIST tests
│   └── nist_suite_v2.py               # v2.0: improved suite with 10M-bit support
├── models/                            # v1.0: energy_model.py, pdr_model.py
├── proofs/                            # v1.0: formal_security.md
├── pipeline/                          # NEW: v2.0 visualization pipeline
│   ├── data_generator.py              # Layer 1
│   ├── plot_engine.py                 # Layer 2 (10 figures)
│   ├── report_builder.py              # Layer 3 (HTML dashboard)
│   └── templates/
│       └── dashboard_template.html
├── scripts/                           # v1.0 + v2.0 report generators
│   ├── generate_complexity_table.py   # v1.0
│   ├── security_report.py             # v1.0
│   ├── ...                            # v1.0 improvements 1-10
│   ├── article_comparison.py          # v1.1: original-vs-improved figures
│   ├── generate_report.py             # v2.0: ONE-COMMAND full pipeline
│   └── compare_versions.py            # v2.0: v2 vs Legacy comparison table
├── visualization/                     # v1.1: comparison_dashboard.py
└── results/
    ├── article_figures/               # v1.1: 12 comparison figures
    ├── figures/                       # v2.0: 10 new figures @ 300 DPI
    ├── raw_data/                      # v2.0: auto-generated CSV/JSON
    └── reports/                       # v2.0: lsa_v2_dashboard.html
```

---

## How to Run

### Prerequisites
```bash
pip install -r requirements.txt
# v2.0 additionally needs: pandas seaborn plotly jinja2
```

### Run v1.0 Baseline / Individual Improvements
```bash
cd lsa_project
python3 main.py
```
Each v1.0 improvement includes a standalone script in `scripts/`:
```bash
python3 scripts/generate_complexity_table.py   # v0.1.0
python3 scripts/security_report.py              # v0.2.0
python3 tests/run_nist_tests.py                 # v0.3.0
...
python3 scripts/verify_proof_assumptions.py     # v1.0.0
```

### Run v2.0 Full Pipeline (Recommended)
```bash
# One command generates all data, figures, and dashboard
python3 scripts/generate_report.py --mode v2

# Output:
#   results/raw_data/*.csv + *.json
#   results/figures/*.png (300 DPI)
#   results/reports/lsa_v2_dashboard.html
```

### Switch Between Cipher Modes
```python
from core.lsa import LSAMode, expand_key, lsa_encrypt_v2, lsa_decrypt_v2

# v2 mode (128-bit, 8 rounds, enhanced f-function)
rkeys = expand_key(0x123456789ABCDEF0011223344556677, mode=LSAMode.V2)
ct = lsa_encrypt_v2(plaintext, rkeys)
pt = lsa_decrypt_v2(ct, rkeys)

# Legacy mode (64-bit, 5 rounds, original paper)
rkeys = expand_key(0x123456789ABCDEF0, mode=LSAMode.LEGACY)
ct = lsa_encrypt(plaintext, rkeys)
```

### CTR Mode Encryption (v2.0)
```python
from core.lsa import ctr_encrypt, ctr_decrypt

message = b"Secret IoT sensor data"
nonce = 0xDEADBEEFCAFEBABE
ciphertext, tag = ctr_encrypt(message, key, nonce, mode=LSAMode.V2)
plaintext = ctr_decrypt(ciphertext, key, nonce, tag, mode=LSAMode.V2)
```

---

## Git Version History

| Version | Improvement | Tag |
|---------|-------------|-----|
| v0.0.0 | Baseline import | `v0.0.0` |
| v0.1.0 | Computational Complexity Analysis | `v0.1.0` |
| v0.2.0 | Theoretical Security Analysis | `v0.2.0` |
| v0.3.0 | NIST SP 800-22 Statistical Tests | `v0.3.0` |
| v0.4.0 | Quantitative Avalanche Analysis | `v0.4.0` |
| v0.5.0 | Analytical Energy Model | `v0.5.0` |
| v0.6.0 | ASCON Standard Comparison | `v0.6.0` |
| v0.7.0 | Key Space & Entropy Analysis | `v0.7.0` |
| v0.8.0 | Side-Channel Resistance | `v0.8.0` |
| v0.9.0 | Analytical PDR Model | `v0.9.0` |
| v1.0.0 | Formal IND-CPA Security Proof | `v1.0.0` |
| v1.0.0-scientific | Final release with comparison report | `v1.0.0-scientific` |
| v1.1.0 | 12 article comparison figures + codebase cleanup | `v1.1.0` |
| **v2.0.0** | **128-bit key, 8 rounds, CTR mode, visualization pipeline** | **`v2.0.0`** |

---

## Citation

> Mahlake et al., "Lightweight Security Algorithm for IoT-based Wireless Sensor Networks," *Journal of Communications*, Vol. 18, No. 1, 2023.
