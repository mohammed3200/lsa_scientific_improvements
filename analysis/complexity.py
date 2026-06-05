"""
Computational Complexity Analysis for LSA, SPN, and Feistel.

Provides operation counts and asymptotic complexity for key expansion
and encryption routines.
"""

from typing import Dict, Any


def key_expansion_complexity() -> Dict[str, Any]:
    """
    Analyze LSA key expansion complexity.

    Returns operation counts for the 64-bit -> 5×16-bit round key schedule.
    """
    # Split 64-bit key into 16 segments of 4 bits
    split_ops = {"mask": 16, "shift": 15}

    # Form 4 Kbif blocks (4 nibbles each)
    concat_ops = {"concat": 4 * 3}  # 3 shifts + OR per block

    # f-function per block: P->Q->P->Q->P->Q (6 layers)
    # Each layer: permutation/transposition + XOR/XNOR + shift
    f_ops = {
        "p_table_perm": 3,      # 3 P-table permutations
        "q_table_trans": 3,     # 3 Q-table transpositions
        "xor": 3,
        "xnor": 2,
        "left_shift": 3,
    }

    # K5 = K1 ^ K2 ^ K3 ^ K4
    k5_ops = {"xor": 4}

    total_ops = {
        "mask": split_ops["mask"],
        "shift": split_ops["shift"] + concat_ops["concat"] + f_ops["left_shift"],
        "xor": f_ops["xor"] + k5_ops["xor"],
        "xnor": f_ops["xnor"],
        "p_table": f_ops["p_table_perm"],
        "q_table": f_ops["q_table_trans"],
        "s_box": 0,  # key expansion does not use S-Box
    }

    return {
        "algorithm": "LSA",
        "phase": "key_expansion",
        "asymptotic": "O(1)",
        "ops_per_function": f_ops,
        "total_operations": sum(total_ops.values()),
        "breakdown": total_ops,
    }


def encryption_complexity() -> Dict[str, Any]:
    """
    Analyze LSA encryption complexity per block.

    Returns per-round and total operation counts for 5 rounds on 64-bit block.
    """
    # Per round: 4 sub-blocks
    # R1_1 = P1 XNOR Ki  -> 1 XNOR
    # EFL = f(R1_1)      -> AND, LS, S-Box(4 nibbles), OR
    # R1_4 = P4 XNOR Ki  -> 1 XNOR
    # EFR = f(R1_4)      -> same as EFL
    # R1_2 = P2 XOR EFL  -> 1 XOR
    # R1_3 = P3 XOR EFR  -> 1 XOR
    # Swap                -> 0 arithmetic ops

    per_round = {
        "xnor": 2,
        "xor": 2,
        "and": 2,       # 2 f-functions, each ANDs 2 bytes
        "left_shift": 2,
        "s_box": 8,     # 2 f-functions × 4 nibbles each
        "or": 2,        # 2 f-functions, each ORs with shifted value
        "swap": 2,      # 2 pair swaps
    }

    rounds = 5
    total = {k: v * rounds for k, v in per_round.items()}

    return {
        "algorithm": "LSA",
        "phase": "encryption",
        "asymptotic": "O(1)",
        "block_size_bits": 64,
        "rounds": rounds,
        "per_round_operations": per_round,
        "total_operations": sum(total.values()),
        "breakdown": total,
    }


def compare_complexity(algo_name: str) -> Dict[str, Any]:
    """
    Return complexity comparison for LSA, SPN, or Feistel.

    Parameters
    ----------
    algo_name : str
        One of 'lsa', 'spn', 'feistel'.

    Returns
    -------
    dict
        Operation count table and asymptotic complexity.
    """
    algo_name = algo_name.lower()

    if algo_name == "lsa":
        key_exp = key_expansion_complexity()
        enc = encryption_complexity()
        return {
            "algorithm": "LSA",
            "key_expansion": key_exp,
            "encryption": enc,
            "summary": {
                "xor_xnor": key_exp["breakdown"]["xor"]
                + key_exp["breakdown"]["xnor"]
                + enc["breakdown"]["xor"]
                + enc["breakdown"]["xnor"],
                "s_box": enc["breakdown"]["s_box"],
                "permutation": key_exp["breakdown"]["p_table"]
                + key_exp["breakdown"]["q_table"],
                "shift": key_exp["breakdown"]["shift"]
                + enc["breakdown"]["left_shift"],
                "total": key_exp["total_operations"] + enc["total_operations"],
            },
        }

    elif algo_name == "spn":
        rounds = 5  # base + key_size/32
        return {
            "algorithm": "SPN",
            "key_expansion": {"asymptotic": "O(r)"},
            "encryption": {
                "asymptotic": "O(r)",
                "rounds": rounds,
                "per_round": {
                    "xor": 1,
                    "s_box": 16,
                    "permutation": 1,
                },
            },
            "summary": {
                "xor_xnor": rounds * 1,
                "s_box": rounds * 16,
                "permutation": rounds * 1,
                "shift": 0,
                "total": rounds * (1 + 16 + 1),
            },
        }

    elif algo_name == "feistel":
        rounds = 8  # base + key_size/32
        return {
            "algorithm": "Feistel",
            "key_expansion": {"asymptotic": "O(r)"},
            "encryption": {
                "asymptotic": "O(r)",
                "rounds": rounds,
                "per_round": {
                    "xor": 1,
                    "s_box": 8,
                    "permutation": 1,
                },
            },
            "summary": {
                "xor_xnor": rounds * 1,
                "s_box": rounds * 8,
                "permutation": rounds * 1,
                "shift": 0,
                "total": rounds * (1 + 8 + 1),
            },
        }

    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")
