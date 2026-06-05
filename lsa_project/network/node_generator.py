"""
WSN Node Generator for 400x400 m² simulation area.
"""

import random
from typing import List, Tuple


def generate_nodes(
    num_nodes: int,
    area_width: float = 400.0,
    area_height: float = 400.0,
    clustered: bool = True,
    num_clusters: int = 4,
    cluster_radius: float = 80.0,
    seed: int = 42,
) -> List[Tuple[float, float]]:
    """
    Generate random node positions.

    Parameters
    ----------
    num_nodes : int
        Number of nodes to place.
    area_width, area_height : float
        Simulation area in meters.
    clustered : bool
        If True, use clustered distribution around centers.
    num_clusters : int
        Number of cluster centers.
    cluster_radius : float
        Radius around each cluster center.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    List[Tuple[float, float]]
        List of (x, y) coordinates.
    """
    random.seed(seed)

    positions = []
    if clustered and num_nodes >= num_clusters:
        # Generate cluster centers
        centers = [
            (
                random.uniform(area_width * 0.2, area_width * 0.8),
                random.uniform(area_height * 0.2, area_height * 0.8),
            )
            for _ in range(num_clusters)
        ]

        nodes_per_cluster = num_nodes // num_clusters
        remainder = num_nodes % num_clusters

        for cidx, (cx, cy) in enumerate(centers):
            count = nodes_per_cluster + (1 if cidx < remainder else 0)
            for _ in range(count):
                angle = random.uniform(0, 2 * 3.141592653589793)
                dist = random.uniform(0, cluster_radius)
                x = cx + dist * (random.uniform(-1, 1))
                y = cy + dist * (random.uniform(-1, 1))
                x = max(0.0, min(area_width, x))
                y = max(0.0, min(area_height, y))
                positions.append((x, y))
    else:
        # Pure random distribution
        for _ in range(num_nodes):
            x = random.uniform(0, area_width)
            y = random.uniform(0, area_height)
            positions.append((x, y))

    random.shuffle(positions)
    return positions[:num_nodes]
