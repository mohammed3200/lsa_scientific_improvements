# Changelog — LSA v2.0

## [2.0.0] — 2025-06-08

### Added

#### Algorithm Upgrades
- **128-bit key support**: `expand_key_v2()` derives 8 round keys from 128-bit master key
- **8-round variant**: `lsa_encrypt_v2()` / `lsa_decrypt_v2()` with enhanced security margin
- **Enhanced f-function**: Additional P-Table layer (`P_TABLE_V2`) and 12-bit left-shift rotation
- **CTR mode**: `ctr_encrypt()` / `ctr_decrypt()` with 64-bit nonce + counter, HMAC-SHA256 AEAD tag
- **Constant-time S-Box**: `constant_time_sbox_lookup()` prevents timing side-channels

#### Visualization Pipeline
- **3-layer architecture**: Data Generator → Plot Engine → Report Builder
- **10 publication-quality figures** at 300 DPI
- **Interactive HTML dashboard** generated via Jinja2 templating
- **One-command report generation**: `python scripts/generate_report.py`

#### Testing
- **NIST SP 800-22 v2 suite**: `tests/nist_suite_v2.py` with 10M-bit support
- **Avalanche analysis**: SAC, BIC, NPCR, UACI measurement
- **Side-channel metrics**: Timing CV, DPA correlation, fault detection

#### Documentation
- `README_v2.md` — v2 usage guide
- `CHANGELOG_v2.md` — version history
- `NIST_VALIDATION.md` — honest test results with explanations

### Changed
- Restructured algorithm code into `core/lsa/` package
- Backward compatibility: Legacy mode preserved in `encrypt_legacy.py`
- Unified color palette and typography across all figures

### Fixed
- CTR mode partial-block handling (last block < 8 bytes)
- `_int_to_bytes()` overflow for 128-bit keys
- NIST CUSUM p-value clamping to [0, 1]
