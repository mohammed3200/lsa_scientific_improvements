"""
Markov-based Analytical PDR Model for WSN.

Fits an exponential decay model to simulated PDR values and provides
prediction capability.
"""

import math
from typing import Dict, Any, List
import numpy as np


def exponential_pdr_model(n_nodes: int, lambda_loss: float) -> float:
    """
    Exponential PDR model: PDR = exp(-λ * N).

    Parameters
    ----------
    n_nodes : int
        Number of nodes in the network.
    lambda_loss : float
        Loss rate parameter per node.

    Returns
    -------
    float
        Predicted PDR in [0, 1].
    """
    return math.exp(-lambda_loss * n_nodes)


def fit_lambda_from_simulation(simulated_pdr: Dict[int, float], n_nodes_list: List[int]) -> float:
    """
    Fit λ using least-squares on log(PDR) vs N.

    Returns the fitted λ that minimizes squared error.
    """
    x = np.array(n_nodes_list, dtype=np.float64)
    y = np.array([math.log(simulated_pdr.get(n, 0.5)) for n in n_nodes_list], dtype=np.float64)

    # Linear fit: log(PDR) = -λ * N  →  y = -λ * x
    # λ = -sum(x*y) / sum(x^2)
    numerator = -np.sum(x * y)
    denominator = np.sum(x ** 2)
    if denominator == 0:
        return 0.001
    return float(numerator / denominator)


def predict_pdr(n_nodes: int, lambda_loss: float) -> float:
    """Predict PDR for any network size given fitted λ."""
    return exponential_pdr_model(n_nodes, lambda_loss)


def validate_pdr_model(
    simulated_pdr: Dict[int, float],
    lambda_loss: float,
    n_nodes_list: List[int],
) -> Dict[int, float]:
    """Return error % between predicted and simulated PDR per node count."""
    errors = {}
    for n in n_nodes_list:
        pred = predict_pdr(n, lambda_loss)
        sim = simulated_pdr.get(n, 0.0)
        if sim > 0:
            errors[n] = abs(pred - sim) / sim * 100.0
        else:
            errors[n] = 0.0
    return errors
