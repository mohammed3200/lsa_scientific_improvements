# GitHub Release Notes — v1.0.0-scientific

**Tag:** `v1.0.0-scientific`  
**Title:** LSA Scientific Hardening — 10 Research Improvements  
**Date:** 2025-06-05

---

## What's New

This release transforms the original LSA empirical simulation into a research-grade cryptographic analysis suite.

### 🔬 10 Scientific Improvements

1. **[Complexity Analysis](analysis/complexity.py)** — Operation counts and O(1) proof for LSA key expansion and encryption.
2. **[Theoretical Security](analysis/security_theory.py)** — Brute-force estimates, differential/linear cryptanalysis bounds, key sensitivity.
3. **[NIST SP 800-22 Tests](tests/nist_suite.py)** — 15 statistical randomness tests on ciphertext output.
4. **[Avalanche Analysis](analysis/avalanche.py)** — SAC, BIC, NPCR, and UACI measurements.
5. **[Energy Model](models/energy_model.py)** — First-order radio model validated against simulation.
6. **[ASCON Comparison](analysis/ascon_comparison.py)** — Feature comparison with NIST lightweight standard.
7. **[Entropy Analysis](analysis/entropy_analysis.py)** — Key collision, Shannon entropy, and chi-square tests.
8. **[Side-Channel Resistance](analysis/side_channel.py)** — Timing, DPA, and fault injection tests.
9. **[PDR Model](models/pdr_model.py)** — Markov-based exponential PDR model.
10. **[Formal Proof](proofs/formal_security.md)** — IND-CPA security proof with reduction to PRESENT S-Box.

### 📊 Deliverables

- `results/fig_master_comparison_dashboard.png` — Side-by-side visualization
- `results/complexity_report.json`
- `results/security_theory_report.json`
- `results/nist_test_results.json` + `nist_summary_table.md`
- `results/avalanche_report.json`
- `results/energy_validation.json`
- `results/ascon_comparison.md`
- `results/entropy_report.json`
- `results/side_channel_report.md`
- `results/pdr_validation.json`
- `results/formal_proof_validation.json`
- `COMPARISON_REPORT.md` — Master audit document

### 🏷️ Version Tags

```
v0.0.0  → Baseline
v0.1.0  → Complexity analysis
v0.2.0  → Theoretical security
v0.3.0  → NIST tests
v0.4.0  → Avalanche analysis
v0.5.0  → Energy model
v0.6.0  → ASCON comparison
v0.7.0  → Entropy analysis
v0.8.0  → Side-channel resistance
v0.9.0  → PDR model
v1.0.0  → Formal security proof
v1.0.0-scientific → Final release
```

### 🚀 How to Use

```bash
pip install -r requirements.txt

# Run individual analyses
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

# Generate dashboard
python3 visualization/comparison_dashboard.py
```

---

**Full documentation:** See `README.md`, `COMPARISON_REPORT.md`, and `CHANGELOG.md`.
