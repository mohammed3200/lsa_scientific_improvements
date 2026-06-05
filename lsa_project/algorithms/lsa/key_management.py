"""
Key Management (Phase 2) — Adopted from SPINS.

Handles:
  - Node authentication
  - MAC generation / verification
  - Counter mode for weak freshness
  - Strong freshness (nonce) handling
  - Power verification before transmission
"""

import hashlib
import secrets
from typing import Dict, Tuple, Optional
from collections import defaultdict


class SPINSKeyManager:
    """
    Simplified SPINS-style key manager.
    """

    def __init__(self):
        # Per-pair counters: counters[(src, dst)] = int
        self.counters: Dict[Tuple[int, int], int] = defaultdict(int)
        # Master secrets per node: secrets[node_id] = bytes
        self.master_secrets: Dict[int, bytes] = {}
        # Nonce store for strong freshness: nonces[(requester, responder)] = nonce_bytes
        self.nonces: Dict[Tuple[int, int], bytes] = {}

    def register_node(self, node_id: int, master_secret: bytes = b"") -> None:
        """Register a node with a master secret."""
        if not master_secret:
            master_secret = secrets.token_bytes(16)
        self.master_secrets[node_id] = master_secret

    def authenticate_pair(self, node_a: int, node_b: int) -> bool:
        """Verify both nodes are registered (legitimacy check)."""
        return node_a in self.master_secrets and node_b in self.master_secrets

    def derive_mac_key(self, node_a: int, node_b: int) -> bytes:
        """Derive a MAC key from combined master secrets."""
        sec_a = self.master_secrets.get(node_a, b"\x00" * 16)
        sec_b = self.master_secrets.get(node_b, b"\x00" * 16)
        combined = sec_a + sec_b
        return hashlib.sha256(combined).digest()[:16]

    def generate_mac(self, src: int, dst: int, encrypted_data: bytes) -> bytes:
        """MAC = MAC(K_mac, Counter || Encrypted_Data)."""
        mac_key = self.derive_mac_key(src, dst)
        counter = self.counters[(src, dst)].to_bytes(4, "big")
        payload = counter + encrypted_data
        return hashlib.sha256(mac_key + payload).digest()[:8]

    def verify_mac(self, src: int, dst: int, encrypted_data: bytes, mac: bytes) -> bool:
        """Verify received MAC."""
        expected = self.generate_mac(src, dst, encrypted_data)
        return secrets.compare_digest(expected, mac)

    def increment_counter(self, src: int, dst: int) -> None:
        """Update counter after transmission."""
        self.counters[(src, dst)] += 1

    def get_counter(self, src: int, dst: int) -> int:
        """Get current counter value."""
        return self.counters[(src, dst)]

    def generate_nonce(self, requester: int, responder: int) -> bytes:
        """Generate a nonce for strong freshness."""
        nonce = secrets.token_bytes(8)
        self.nonces[(requester, responder)] = nonce
        return nonce

    def get_nonce(self, requester: int, responder: int) -> Optional[bytes]:
        """Retrieve stored nonce."""
        return self.nonces.get((requester, responder))

    def compute_mac_with_nonce(self, src: int, dst: int, encrypted_data: bytes) -> bytes:
        """
        Include nonce in MAC computation for strong freshness response.
        Nonce is NOT returned in plaintext.
        """
        nonce = self.nonces.get((src, dst), b"")
        mac_key = self.derive_mac_key(src, dst)
        counter = self.counters[(src, dst)].to_bytes(4, "big")
        payload = counter + nonce + encrypted_data
        return hashlib.sha256(mac_key + payload).digest()[:8]


class PowerVerifier:
    """
    Power verification before transmission.
    Ensures En >= Eth for all nodes; discards packets if insufficient.
    """

    def __init__(self, threshold_uj: float = 100.0):
        self.threshold = threshold_uj

    def check_node(self, energy_remaining_uj: float) -> bool:
        """Return True if node has sufficient energy."""
        return energy_remaining_uj >= self.threshold

    def verify_network(self, energies: Dict[int, float]) -> Tuple[bool, list]:
        """
        Check all nodes in network.
        Returns (all_ok, list_of_low_energy_nodes).
        """
        low_nodes = [n for n, e in energies.items() if e < self.threshold]
        return len(low_nodes) == 0, low_nodes
