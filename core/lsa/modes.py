"""
LSA v2 Mode of Operation — CTR (Counter) Mode with AEAD.

CTR Mode:
    Ciphertext[i] = Plaintext[i] ^ LSA(Nonce || Counter_i)

AEAD Tag:
    Uses HMAC-SHA256 for authentication.
    In a real lightweight implementation, CMAC-AES or KMAC would be used.
"""

import struct
import hashlib
import hmac
from typing import Tuple

from .constants import LSAMode
from .key_expansion import expand_key
from .encrypt_v2 import lsa_encrypt_v2
from .encrypt_legacy import lsa_encrypt


def _incr_counter(counter: int) -> int:
    """Increment 64-bit counter with wrap-around."""
    return (counter + 1) & 0xFFFFFFFFFFFFFFFF


def _make_nonce_ctr_block(nonce: int, counter: int) -> int:
    """Combine 64-bit nonce and 64-bit counter into a 128-bit block."""
    return ((nonce & 0xFFFFFFFFFFFFFFFF) << 64) | (counter & 0xFFFFFFFFFFFFFFFF)


def _split_into_blocks(data: bytes, block_size: int = 8) -> list:
    """Split byte data into blocks of specified size."""
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]


def _bytes_to_int(block: bytes) -> int:
    """Convert bytes to integer (big-endian)."""
    return int.from_bytes(block, 'big')


def _int_to_bytes(value: int, length: int = 8) -> bytes:
    """Convert integer to bytes (big-endian), masking to fit length."""
    value = value & ((1 << (length * 8)) - 1)
    return value.to_bytes(length, 'big')


def ctr_encrypt(plaintext: bytes, key: int, nonce: int, mode: str = LSAMode.V2) -> Tuple[bytes, bytes]:
    """
    CTR mode encryption for LSA.

    Parameters
    ----------
    plaintext : bytes
        Message to encrypt (arbitrary length).
    key : int
        Master cipher key (64-bit for legacy, 128-bit for v2).
    nonce : int
        64-bit nonce (must be unique per message under the same key).
    mode : str
        LSAMode.LEGACY or LSAMode.V2.

    Returns
    -------
    tuple
        (ciphertext_bytes, tag_bytes)
    """
    round_keys = expand_key(key, mode=mode)
    encrypt_fn = lsa_encrypt if mode == LSAMode.LEGACY else lsa_encrypt_v2

    blocks = _split_into_blocks(plaintext, 8)
    counter = 0
    ciphertext = b''

    for block in blocks:
        # Generate keystream block: LSA(nonce || counter)
        # We XOR the lower 64 bits of the 128-bit nonce+ctr with the plaintext block
        nonce_ctr = _make_nonce_ctr_block(nonce, counter)
        keystream_input = nonce_ctr & 0xFFFFFFFFFFFFFFFF  # Take lower 64 bits for LSA block
        keystream = encrypt_fn(keystream_input, round_keys)

        # XOR plaintext block with keystream
        pt_block_int = _bytes_to_int(block)
        ct_block_int = (pt_block_int ^ keystream) & ((1 << (len(block) * 8)) - 1)
        ct_block = _int_to_bytes(ct_block_int, len(block))
        ciphertext += ct_block

        counter = _incr_counter(counter)

    # Generate authentication tag using HMAC-SHA256
    # In production, use a lightweight MAC like CMAC or Poly1305
    key_bytes = _int_to_bytes(key, 16 if mode == LSAMode.V2 else 8)
    tag = hmac.new(key_bytes, ciphertext, hashlib.sha256).digest()

    return ciphertext, tag


def ctr_decrypt(ciphertext: bytes, key: int, nonce: int, tag: bytes, mode: str = LSAMode.V2) -> bytes:
    """
    CTR mode decryption for LSA.

    Parameters
    ----------
    ciphertext : bytes
        Encrypted message.
    key : int
        Master cipher key.
    nonce : int
        64-bit nonce used during encryption.
    tag : bytes
        Authentication tag from encryption.
    mode : str
        LSAMode.LEGACY or LSAMode.V2.

    Returns
    -------
    bytes
        Decrypted plaintext.

    Raises
    ------
    ValueError
        If authentication tag verification fails.
    """
    # Verify tag first
    key_bytes = _int_to_bytes(key, 16 if mode == LSAMode.V2 else 8)
    expected_tag = hmac.new(key_bytes, ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Authentication tag verification failed — message may be tampered.")

    round_keys = expand_key(key, mode=mode)
    encrypt_fn = lsa_encrypt if mode == LSAMode.LEGACY else lsa_encrypt_v2

    blocks = _split_into_blocks(ciphertext, 8)
    counter = 0
    plaintext = b''

    for block in blocks:
        nonce_ctr = _make_nonce_ctr_block(nonce, counter)
        keystream_input = nonce_ctr & 0xFFFFFFFFFFFFFFFF
        keystream = encrypt_fn(keystream_input, round_keys)

        ct_block_int = _bytes_to_int(block)
        pt_block_int = (ct_block_int ^ keystream) & ((1 << (len(block) * 8)) - 1)
        pt_block = _int_to_bytes(pt_block_int, len(block))
        plaintext += pt_block

        counter = _incr_counter(counter)

    # Strip PKCS#7-like padding (null bytes) — in a real system use proper padding
    return plaintext.rstrip(b'\x00')
