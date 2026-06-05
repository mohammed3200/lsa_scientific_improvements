# LSA Scientific Improvements

**Project:** Lightweight Security Algorithm (LSA) — Research-Grade Hardening  
**Reference:** Mahlake et al., *Journal of Communications*, Vol. 18, No. 1, 2023  
**License:** MIT

---

## Overview

This repository contains a scientifically hardened implementation of the LSA (Lightweight Security Algorithm) hybrid cipher for Wireless Sensor Networks (WSNs) in IoT. It extends the original four-metric simulation (key expansion time, security level, energy consumption, packet delivery ratio) with ten research-grade improvements, including formal proofs, NIST statistical validation, complexity analysis, and modern standard comparison.

---

## Baseline Description

The original LSA implementation provides:
- **Algorithm:** LSA hybrid cipher (SIT key expansion + SPINS key management)
- **Parameters:** 64-bit block, 64-bit key, 5 rounds, 4×4 S-Box
- **Baselines:** SPN and Feistel Network for comparative evaluation
- **Metrics:** Four publication-quality graphs (key expansion, security, energy, PDR)
- **Simulation:** 100 nodes, 400×400 m², IEEE 802.11s model, 10-run averaging

---

## Directory Map

```
lsa_scientific_improvements/
├── README.md                    # This file
├── BASELINE.md                  # Baseline state tracker
├── CHANGELOG.md                 # Version history
├── requirements.txt             # Python dependencies
├── GITHUB_SETUP.md              # Git remote and branching guide
├── lsa_project/                 # Original LSA implementation
│   ├── main.py
│   ├── config.py
│   ├── algorithms/
│   ├── network/
│   ├── metrics/
│   └── visualization/
├── analysis/                    # New: complexity, security, avalanche
├── tests/                       # New: NIST SP 800-22 suite
├── models/                      # New: analytical energy and PDR models
├── proofs/                      # New: formal security proofs
├── scripts/                     # New: report generators
├── visualization/               # New: comparison dashboard
└── results/                     # Generated outputs
```

---

## How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run Baseline Simulation
```bash
cd lsa_project
python3 main.py
```

### Run Individual Improvements
Each improvement includes a standalone script in `scripts/`:
```bash
python3 scripts/generate_complexity_table.py
python3 scripts/security_report.py
python3 tests/run_nist_tests.py
python3 scripts/avalanche_report.py
python3 scripts/validate_energy.py
python3 scripts/ascon_report.py
python3 scripts/entropy_report.py
python3 scripts/side_channel_report.py
python3 scripts/validate_pdr.py
python3 scripts/verify_proof_assumptions.py
```

### Generate Final Comparison Report
```bash
python3 visualization/comparison_dashboard.py
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

---

## Citation

> Mahlake et al., "Lightweight Security Algorithm for IoT-based Wireless Sensor Networks," *Journal of Communications*, Vol. 18, No. 1, 2023.
