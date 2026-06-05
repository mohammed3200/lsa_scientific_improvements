# GitHub Remote Setup and Branching Strategy

## Repository Name
`lsa-scientific-improvements`

## Push to Remote

```bash
git remote add origin https://github.com/YOUR_USERNAME/lsa-scientific-improvements.git
git push -u origin main
```

## Branching Strategy

- **`main`** — Protected branch. Only merged feature branches allowed.
- **Feature branches** — Each improvement gets its own branch:
  - `feat/improvement-1-complexity-analysis`
  - `feat/improvement-2-theoretical-security`
  - `feat/improvement-3-nist-tests`
  - `feat/improvement-4-avalanche`
  - `feat/improvement-5-energy-model`
  - `feat/improvement-6-ascon-comparison`
  - `feat/improvement-7-entropy`
  - `feat/improvement-8-side-channel`
  - `feat/improvement-9-pdr-model`
  - `feat/improvement-10-formal-proof`

## Workflow

1. Create feature branch from `main`.
2. Implement improvement.
3. Commit with conventional commit message.
4. Merge into `main` via fast-forward.
5. Tag the merge commit with semantic version.

## Tags

| Tag | Description |
|-----|-------------|
| `v0.0.0` | Baseline import |
| `v0.1.0` | Complexity analysis |
| `v0.2.0` | Theoretical security |
| `v0.3.0` | NIST statistical tests |
| `v0.4.0` | Avalanche analysis |
| `v0.5.0` | Analytical energy model |
| `v0.6.0` | ASCON comparison |
| `v0.7.0` | Entropy analysis |
| `v0.8.0` | Side-channel resistance |
| `v0.9.0` | Analytical PDR model |
| `v1.0.0` | Formal security proof |
| `v1.0.0-scientific` | Final release with comparison report |
