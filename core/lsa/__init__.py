"""
LSA v2.0 Core Package
=====================
Lightweight Security Algorithm with 128-bit key, 8 rounds, CTR mode.

Exports:
    LSAMode, DEFAULT_MODE
    expand_key, expand_key_v2, expand_key_legacy, expand_key_scaled
    lsa_encrypt, lsa_decrypt (legacy)
    lsa_encrypt_v2, lsa_decrypt_v2 (v2)
    ctr_encrypt, ctr_decrypt (CTR mode with AEAD)
    constant_time_sbox_lookup (side-channel resistant)
"""

from .constants import LSAMode, DEFAULT_MODE
from .key_expansion import expand_key, expand_key_v2, expand_key_legacy, expand_key_scaled
from .encrypt_legacy import lsa_encrypt, lsa_decrypt
from .encrypt_v2 import lsa_encrypt_v2, lsa_decrypt_v2
from .modes import ctr_encrypt, ctr_decrypt
from .s_box import constant_time_sbox_lookup
from .sensor_data import (
    read_system_sensors,
    pack_sensor_block,
    unpack_sensor_block,
    generate_realistic_sensor_data,
    generate_sensor_stream,
    describe_sensor_block,
)

__all__ = [
    "LSAMode",
    "DEFAULT_MODE",
    "expand_key",
    "expand_key_v2",
    "expand_key_legacy",
    "expand_key_scaled",
    "lsa_encrypt",
    "lsa_decrypt",
    "lsa_encrypt_v2",
    "lsa_decrypt_v2",
    "ctr_encrypt",
    "ctr_decrypt",
    "constant_time_sbox_lookup",
    "read_system_sensors",
    "pack_sensor_block",
    "unpack_sensor_block",
    "generate_realistic_sensor_data",
    "generate_sensor_stream",
    "describe_sensor_block",
]
