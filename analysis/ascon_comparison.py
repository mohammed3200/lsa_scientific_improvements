"""
Comparison between LSA and NIST ASCON-128 Lightweight Standard.

Generates feature comparison and upgrade recommendations.
"""

from typing import Dict, Any, List


def ascon_comparison_table() -> List[Dict[str, str]]:
    """Return structured comparison table."""
    return [
        {"Feature": "Algorithm Type", "ASCON-128": "Sponge-based AEAD", "LSA (Current)": "Feistel-like block cipher", "LSA (Recommended)": "Sponge or Tweakable block cipher"},
        {"Feature": "Key Size", "ASCON-128": "128-bit", "LSA (Current)": "64-bit", "LSA (Recommended)": "128-bit"},
        {"Feature": "Nonce Size", "ASCON-128": "128-bit", "LSA (Current)": "N/A", "LSA (Recommended)": "64-bit"},
        {"Feature": "Tag Size", "ASCON-128": "128-bit", "LSA (Current)": "64-bit (MAC)", "LSA (Recommended)": "128-bit"},
        {"Feature": "Rounds", "ASCON-128": "12 (a+b)", "LSA (Current)": "5", "LSA (Recommended)": "8-10"},
        {"Feature": "AEAD Support", "ASCON-128": "Yes", "LSA (Current)": "No", "LSA (Recommended)": "Yes"},
        {"Feature": "NIST Standard", "ASCON-128": "Yes (2023/2025)", "LSA (Current)": "No", "LSA (Recommended)": "Candidate"},
        {"Feature": "Security Level", "ASCON-128": "128-bit", "LSA (Current)": "64-bit", "LSA (Recommended)": "128-bit"},
        {"Feature": "Energy per Block", "ASCON-128": "~0.12 μJ", "LSA (Current)": "~0.056 μJ", "LSA (Recommended)": "~0.10 μJ"},
        {"Feature": "Code Size", "ASCON-128": "~2 KB", "LSA (Current)": "~1.5 KB", "LSA (Recommended)": "~2.5 KB"},
    ]


def security_margin_analysis(ops_per_sec: float = 1e15) -> Dict[str, Any]:
    """Analyze breaking time on a GPU cluster."""
    return {
        "ascon_128": {
            "key_space": 2 ** 128,
            "avg_trials": 2 ** 127,
            "time_years": (2 ** 127) / (ops_per_sec * 365.25 * 86400),
        },
        "lsa_64": {
            "key_space": 2 ** 64,
            "avg_trials": 2 ** 63,
            "time_years": (2 ** 63) / (ops_per_sec * 365.25 * 86400),
        },
        "lsa_128_recommended": {
            "key_space": 2 ** 128,
            "avg_trials": 2 ** 127,
            "time_years": (2 ** 127) / (ops_per_sec * 365.25 * 86400),
        },
    }
