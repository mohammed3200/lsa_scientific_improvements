"""
LSA Decryption re-exports from encrypt.py for convenience.
The decrypt logic lives in encrypt.py because encryption and decryption
share the same Feistel-like structure.
"""

from .encrypt import lsa_decrypt

__all__ = ["lsa_decrypt"]
