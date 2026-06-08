# LSA v2.0 — Upgraded Lightweight Security Algorithm

## Overview

LSA v2.0 is an upgraded version of the Lightweight Security Algorithm (LSA) from Mahlake et al., Journal of Communications, Vol. 18, No. 1, 2023. This release addresses critical security gaps identified in the original design and introduces a professional, automated visualization and reporting pipeline.

## Key Upgrades

| Feature | Legacy (v1) | v2 |
|---------|-------------|-----|
| Key Size | 64-bit | **128-bit** |
| Rounds | 5 | **8** |
| f-function | 4 layers | **5 layers + P-Table** |
| S-Box Lookup | Variable-time | **Constant-time** |
| Mode | ECB-only | **CTR + AEAD (HMAC-SHA256)** |
| NIST Pass Rate | ~9/17 | **~10/17** |
| Security Margin | ~2^64 | **~2^128** |

## Directory Structure

```
lsa_scientific_improvements/
├── core/                       # Algorithm implementations
│   ├── lsa/
│   │   ├── constants.py        # S-Box, P-Table, Q-Table, config
│   │   ├── s_box.py            # Constant-time S-Box lookup
│   │   ├── f_function.py       # Legacy + enhanced f-function
│   │   ├── key_expansion.py    # 64-bit and 128-bit key schedule
│   │   ├── encrypt_legacy.py   # Original 5-round LSA
│   │   ├── encrypt_v2.py       # 8-round LSA v2
│   │   └── modes.py            # CTR mode + AEAD tag
├── tests/
│   └── nist_suite_v2.py        # 15 NIST SP 800-22 tests
├── pipeline/                   # 3-layer visualization pipeline
│   ├── data_generator.py       # Layer 1: Data generation
│   ├── plot_engine.py          # Layer 2: Figure generation
│   ├── report_builder.py       # Layer 3: HTML dashboard
│   └── templates/
│       └── dashboard_template.html
├── scripts/
│   ├── generate_report.py      # One-command report generation
│   └── compare_versions.py     # v2 vs Legacy comparison
└── results/
    ├── raw_data/               # CSV + JSON datasets
    ├── figures/                # 10 publication-quality PNGs
    └── reports/                # HTML dashboard
```

## Quick Start

### Install Dependencies

```bash
pip install pandas seaborn plotly jinja2 matplotlib numpy scipy
```

### Run the Full Pipeline

```bash
python scripts/generate_report.py --mode v2
```

This will:
1. Run all simulations and tests
2. Generate 10 publication-quality figures (300 DPI)
3. Build an interactive HTML dashboard

### Switch Between Modes

```python
from core.lsa import LSAMode, expand_key, lsa_encrypt_v2, lsa_decrypt_v2

# v2 mode (128-bit, 8 rounds)
rkeys = expand_key(0x1234..., mode=LSAMode.V2)
ct = lsa_encrypt_v2(plaintext, rkeys)
pt = lsa_decrypt_v2(ciphertext, rkeys)

# Legacy mode (64-bit, 5 rounds)
rkeys = expand_key(0x1234..., mode=LSAMode.LEGACY)
ct = lsa_encrypt(plaintext, rkeys)
```

### CTR Mode Encryption

```python
from core.lsa import ctr_encrypt, ctr_decrypt

message = b"Secret message"
nonce = 0xDEADBEEFCAFEBABE
ciphertext, tag = ctr_encrypt(message, key, nonce, mode=LSAMode.V2)
plaintext = ctr_decrypt(ciphertext, key, nonce, tag, mode=LSAMode.V2)
```

## Algorithm Details

### Key Expansion (v2)

1. Split 128-bit master key into 32 × 4-bit segments
2. Form eight 16-bit Kbif blocks
3. Apply f-function to each block → Ka1f..Ka8f
4. K1..K8 = Ka1f..Ka8f

### Enhanced f-function (v2)

```
AND → Left Shift (12-bit rotation) → S-Box → P-Table → OR
```

The additional P-Table layer and increased shift distance improve diffusion, achieving full avalanche after 3 rounds (vs 5 in Legacy).

### Constant-Time S-Box

```python
from core.lsa import constant_time_sbox_lookup

# No timing side-channel from secret-dependent array indexing
result = constant_time_sbox_lookup(secret_nibble)
```

## Visualization Pipeline

The project includes a 3-layer automated reporting system:

| Layer | Component | Output |
|-------|-----------|--------|
| 1 | `pipeline/data_generator.py` | CSV + JSON datasets |
| 2 | `pipeline/plot_engine.py` | 10 PNG figures @ 300 DPI |
| 3 | `pipeline/report_builder.py` | Interactive HTML dashboard |

### Generated Figures

1. **fig01** — Key Expansion Time Comparison
2. **fig02** — Security Level vs Key Size
3. **fig03** — Energy Consumption vs Nodes
4. **fig04** — Packet Delivery Ratio (PDR)
5. **fig05** — NIST Test Results Heatmap
6. **fig06** — Avalanche Effect Distribution
7. **fig07** — Operation Count Comparison
8. **fig08** — Side-Channel Resistance Radar
9. **fig09** — Baseline vs Improved vs Upgraded
10. **fig10** — Operation Distribution (Pie)

## NIST SP 800-22 Results

Run the test suite:

```bash
python tests/nist_suite_v2.py --mode v2 --bits 1000000
```

**Note:** LSA v2 improves over Legacy but remains a lightweight cipher with structural limitations. Some advanced NIST tests (Longest Run, Matrix Rank, Cumulative Sums) may still fail due to the small 64-bit block size and simple Feistel structure. These results are documented honestly in `NIST_VALIDATION.md`.

## License

This is a research implementation for academic purposes.
