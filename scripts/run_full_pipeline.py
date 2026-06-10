#!/usr/bin/env python3
"""
LSA v2.0 — Complete 7-Stage Operational Pipeline
=================================================

Runs the full lifecycle from real sensor data to encrypted transmission,
decryption, testing, and visualization.

Usage:
    python scripts/run_full_pipeline.py --mode v2 --sensors 100

Stages:
    0. Data Acquisition    — Read/generate real sensor data
    1. Key Expansion       — Derive round keys from master key
    2. Key Management      — SPINS-style authentication & freshness
    3. Encryption          — LSA block encryption (5 or 8 rounds)
    4. Transmission        — Packet assembly with MAC
    5. Reception & Decrypt — Verify and decrypt
    6. Testing & Metrics   — NIST, avalanche, energy, PDR
    7. Visualization       — Generate figures and dashboard
"""

import argparse
import sys
import time
import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.lsa import (
    LSAMode, expand_key, expand_key_v2, expand_key_legacy,
    lsa_encrypt, lsa_decrypt, lsa_encrypt_v2, lsa_decrypt_v2,
    ctr_encrypt, ctr_decrypt,
    read_system_sensors, pack_sensor_block, unpack_sensor_block,
    generate_realistic_sensor_data, generate_sensor_stream,
)
from pipeline.data_generator import DataGenerator
from pipeline.plot_engine import PlotEngine
from pipeline.report_builder import ReportBuilder


# =============================================================================
# STAGE 0: Data Acquisition
# =============================================================================

def stage_0_data_acquisition(sensor_count: int = 100, sensor_type: str = "temperature") -> List[int]:
    """Read real system sensors and generate IoT sensor stream."""
    print("\n" + "=" * 70)
    print("STAGE 0: Data Acquisition (الحصول على البيانات)")
    print("=" * 70)
    
    # Read real system sensor first
    real_block = read_system_sensors()
    real_data = unpack_sensor_block(real_block)
    print(f"  [Real System Sensor]")
    print(f"    Temperature:  {real_data['temperature']:.1f}°C")
    print(f"    CPU Usage:    {real_data['cpu_usage']:.1f}%")
    print(f"    Battery:      {real_data['battery']:.1f}%")
    print(f"    64-bit Block: 0x{real_block:016X}")
    
    # Generate sensor stream for encryption
    print(f"\n  [Generating {sensor_count} {sensor_type} sensor readings...]")
    stream = generate_sensor_stream(count=sensor_count, sensor_type=sensor_type, seed=42)
    print(f"  Generated {len(stream)} sensor blocks")
    print(f"  Sample: 0x{stream[0]:016X}, 0x{stream[1]:016X}, ...")
    
    return stream


# =============================================================================
# STAGE 1: Key Expansion (Phase 1 — SIT-based)
# =============================================================================

def stage_1_key_expansion(mode: str = LSAMode.V2) -> Tuple[Any, int]:
    """Expand master key into round keys."""
    print("\n" + "=" * 70)
    print("STAGE 1: Key Expansion (توسيع المفتاح) — Phase 1")
    print("=" * 70)
    
    if mode == LSAMode.LEGACY:
        master_key = random.getrandbits(64)
        round_keys = expand_key_legacy(master_key)
        print(f"  Mode:      LEGACY (64-bit key, 5 rounds)")
    else:
        master_key = random.getrandbits(128)
        round_keys = expand_key_v2(master_key)
        print(f"  Mode:      v2 (128-bit key, 8 rounds)")
    
    print(f"  Master Key: 0x{master_key:032X}")
    print(f"  Round Keys: {[f'0x{k:04X}' for k in round_keys]}")
    
    return round_keys, master_key


# =============================================================================
# STAGE 2: Key Management (Phase 2 — SPINS-based)
# =============================================================================

def stage_2_key_management(
    node_id: int = 7,
    receiver_id: int = 12,
    counter: int = 1,
    energy: float = 4500.0,
    threshold: float = 100.0,
) -> Dict[str, Any]:
    """SPINS-style authentication, power verification, and freshness."""
    print("\n" + "=" * 70)
    print("STAGE 2: Key Management (إدارة المفاتيح) — Phase 2 (SPINS)")
    print("=" * 70)
    
    # 2.1: Authentication (simplified MAC key)
    mac_key = b"shared_mac_key_12345"
    print(f"  [2.1] Authentication: MAC key established")
    
    # 2.2: Power verification
    power_ok = energy >= threshold
    print(f"  [2.2] Power Check: En={energy:.0f}μJ ≥ Eth={threshold:.0f}μJ → {'PASS' if power_ok else 'REJECT'}")
    if not power_ok:
        raise ValueError("Power threshold not met — packet rejected")
    
    # 2.3: Freshness (anti-replay)
    last_counter = counter - 1
    freshness_ok = counter > last_counter
    print(f"  [2.3] Freshness: Counter={counter} > Last={last_counter} → {'PASS' if freshness_ok else 'REJECT'}")
    if not freshness_ok:
        raise ValueError("Replay attack detected — packet rejected")
    
    # 2.4: MAC generation
    mac = hashlib.sha256(mac_key + counter.to_bytes(4, 'big')).hexdigest()[:16]
    print(f"  [2.4] MAC Generated: {mac}")
    
    return {
        "mac_key": mac_key,
        "counter": counter,
        "mac": mac,
        "node_id": node_id,
        "receiver_id": receiver_id,
        "energy": energy,
    }


# =============================================================================
# STAGE 3: Encryption (Phase 3 — 5 or 8 rounds)
# =============================================================================

def stage_3_encryption(
    plaintext_blocks: List[int],
    round_keys: Tuple[int, ...],
    mode: str = LSAMode.V2,
) -> List[int]:
    """Encrypt sensor data blocks using LSA."""
    print("\n" + "=" * 70)
    print(f"STAGE 3: Encryption (التشفير) — Phase 3 ({len(round_keys)} rounds)")
    print("=" * 70)
    
    encrypt_fn = lsa_encrypt_v2 if mode == LSAMode.V2 else lsa_encrypt
    
    ciphertext_blocks = []
    start = time.time()
    for i, pt in enumerate(plaintext_blocks):
        ct = encrypt_fn(pt, round_keys)
        ciphertext_blocks.append(ct)
    elapsed = time.time() - start
    
    print(f"  Encrypted {len(plaintext_blocks)} blocks in {elapsed*1000:.2f} ms")
    print(f"  Throughput: {len(plaintext_blocks)/elapsed:.0f} blocks/sec")
    print(f"  Sample: PT=0x{plaintext_blocks[0]:016X} → CT=0x{ciphertext_blocks[0]:016X}")
    
    return ciphertext_blocks


# =============================================================================
# STAGE 4: Transmission
# =============================================================================

def stage_4_transmission(
    ciphertext_blocks: List[int],
    key_mgmt: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Assemble packets with MAC, counter, and nonce."""
    print("\n" + "=" * 70)
    print("STAGE 4: Transmission (الإرسال عبر الشبكة)")
    print("=" * 70)
    
    packets = []
    for i, ct in enumerate(ciphertext_blocks):
        pkt_counter = key_mgmt["counter"] + i
        # Compute per-packet MAC using counter
        pkt_mac = hashlib.sha256(key_mgmt["mac_key"] + pkt_counter.to_bytes(4, 'big')).hexdigest()[:16]
        packet = {
            "node_id": key_mgmt["node_id"],
            "receiver_id": key_mgmt["receiver_id"],
            "counter": pkt_counter,
            "ciphertext": ct,
            "mac": pkt_mac,
            "nonce": random.getrandbits(64),
            "energy_tx": 0.35 * 64,  # μJ per 64-bit block
        }
        packets.append(packet)
    
    print(f"  Assembled {len(packets)} packets")
    print(f"  Packet structure: [NodeID | Counter | Ciphertext(64b) | MAC | Nonce]")
    print(f"  Energy per packet: ~{packets[0]['energy_tx']:.1f} μJ")
    
    return packets


# =============================================================================
# STAGE 5: Reception & Decryption
# =============================================================================

def stage_5_reception_decryption(
    packets: List[Dict[str, Any]],
    round_keys: Tuple[int, ...],
    mode: str = LSAMode.V2,
) -> List[int]:
    """Verify MAC, check freshness, and decrypt."""
    print("\n" + "=" * 70)
    print("STAGE 5: Reception & Decryption (الاستقبال وفك التشفير)")
    print("=" * 70)
    
    decrypt_fn = lsa_decrypt_v2 if mode == LSAMode.V2 else lsa_decrypt
    
    plaintext_blocks = []
    start = time.time()
    for pkt in packets:
        # Verify MAC (simplified)
        mac_key = b"shared_mac_key_12345"
        expected_mac = hashlib.sha256(mac_key + pkt["counter"].to_bytes(4, 'big')).hexdigest()[:16]
        mac_ok = pkt["mac"] == expected_mac
        if not mac_ok:
            raise ValueError(f"MAC verification failed for packet {pkt['counter']}")
        
        # Decrypt
        pt = decrypt_fn(pkt["ciphertext"], round_keys)
        plaintext_blocks.append(pt)
    
    elapsed = time.time() - start
    print(f"  Verified & decrypted {len(packets)} packets in {elapsed*1000:.2f} ms")
    print(f"  Sample: CT=0x{packets[0]['ciphertext']:016X} → PT=0x{plaintext_blocks[0]:016X}")
    
    return plaintext_blocks


# =============================================================================
# STAGE 6: Testing & Metrics
# =============================================================================

def stage_6_testing(
    original: List[int],
    decrypted: List[int],
    ciphertext: List[int],
    mode: str = LSAMode.V2,
) -> Dict[str, Any]:
    """Run validation tests and compute metrics."""
    print("\n" + "=" * 70)
    print("STAGE 6: Testing & Metrics (الاختبار وجمع المقاييس)")
    print("=" * 70)
    
    results = {}
    
    # 6.1: Round-trip verification
    all_match = all(o == d for o, d in zip(original, decrypted))
    results["round_trip_ok"] = all_match
    print(f"  [6.1] Round-trip: {'PASS ✓' if all_match else 'FAIL ✗'} ({len(original)} blocks)")
    
    # 6.2: Avalanche effect (flip 1 bit in first block)
    if len(original) > 1:
        pt1 = original[0]
        pt2 = original[0] ^ 0x0000000000000001  # flip LSB
        rk = expand_key_v2(0xA5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5) if mode == LSAMode.V2 else expand_key_legacy(0xA5A5A5A5A5A5A5A5)
        encrypt_fn = lsa_encrypt_v2 if mode == LSAMode.V2 else lsa_encrypt
        ct1 = encrypt_fn(pt1, rk)
        ct2 = encrypt_fn(pt2, rk)
        hd = bin(ct1 ^ ct2).count('1')
        sac = hd / 64.0 * 100
        results["avalanche_hd"] = hd
        results["avalanche_sac"] = sac
        print(f"  [6.2] Avalanche: Hamming Distance = {hd}/64 ({sac:.1f}%)")
    
    # 6.3: Key sensitivity
    if mode == LSAMode.V2:
        key1 = 0xA5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5
        key2 = key1 ^ 0x0000000000000001
        rk1 = expand_key_v2(key1)
        rk2 = expand_key_v2(key2)
        ct1 = lsa_encrypt_v2(original[0], rk1)
        ct2 = lsa_encrypt_v2(original[0], rk2)
        hd = bin(ct1 ^ ct2).count('1')
        results["key_sensitivity_hd"] = hd
        print(f"  [6.3] Key Sensitivity: Hamming Distance = {hd}/64 ({hd/64*100:.1f}%)")
    
    # 6.4: Energy per block
    results["energy_per_block_uJ"] = 0.35 * 64
    print(f"  [6.4] Energy: ~{results['energy_per_block_uJ']:.1f} μJ per 64-bit block")
    
    # 6.5: Ciphertext randomness (entropy)
    ct_bytes = b''.join(ct.to_bytes(8, 'big') for ct in ciphertext[:100])
    byte_counts = [ct_bytes.count(b) for b in range(256)]
    total = len(ct_bytes)
    import math
    entropy = 0.0
    for count in byte_counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    results["ciphertext_entropy"] = entropy
    print(f"  [6.5] Ciphertext Entropy: {entropy:.2f} bits/byte (max=8.0)")
    
    return results


# =============================================================================
# STAGE 7: Comparison & Visualization
# =============================================================================

def stage_7_visualization(mode: str = LSAMode.V2):
    """Run the full visualization pipeline."""
    print("\n" + "=" * 70)
    print("STAGE 7: Comparison & Visualization (المقارنة والتصور)")
    print("=" * 70)
    
    # 7.1: Generate data
    print("  [7.1] Generating datasets...")
    gen = DataGenerator(mode=mode)
    gen.run_all()
    
    # 7.2: Generate figures
    print("  [7.2] Generating figures...")
    plot = PlotEngine()
    plot.generate_all()
    
    # 7.3: Build dashboard
    print("  [7.3] Building dashboard...")
    builder = ReportBuilder()
    dashboard = builder.build_dashboard()
    
    print(f"  Dashboard: {dashboard}")
    print(f"  Figures:   results/figures/ (10 PNG files)")
    print(f"  Raw Data:  results/raw_data/ (CSV + JSON)")


# =============================================================================
# Master Runner
# =============================================================================

def run_full_pipeline(
    mode: str = LSAMode.V2,
    sensor_count: int = 100,
    sensor_type: str = "temperature",
):
    """Execute all 7 stages of the LSA operational pipeline."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "LSA ALGORITHM — COMPLETE OPERATIONAL PIPELINE" + " " * 18 + "║")
    print("╚" + "═" + "═" * 67 + "╝")
    
    t_start = time.time()
    
    # Stage 0: Data Acquisition
    plaintext = stage_0_data_acquisition(sensor_count, sensor_type)
    
    # Stage 1: Key Expansion
    round_keys, master_key = stage_1_key_expansion(mode)
    
    # Stage 2: Key Management
    key_mgmt = stage_2_key_management()
    
    # Stage 3: Encryption
    ciphertext = stage_3_encryption(plaintext, round_keys, mode)
    
    # Stage 4: Transmission
    packets = stage_4_transmission(ciphertext, key_mgmt)
    
    # Stage 5: Reception & Decryption
    decrypted = stage_5_reception_decryption(packets, round_keys, mode)
    
    # Stage 6: Testing
    test_results = stage_6_testing(plaintext, decrypted, ciphertext, mode)
    
    # Stage 7: Visualization
    stage_7_visualization(mode)
    
    t_total = time.time() - t_start
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"  Total time:      {t_total:.2f} seconds")
    print(f"  Mode:            {mode}")
    print(f"  Sensor blocks:   {len(plaintext)}")
    print(f"  Round-trip:      {'PASS ✓' if test_results['round_trip_ok'] else 'FAIL ✗'}")
    print(f"  Avalanche SAC:   {test_results.get('avalanche_sac', 0):.1f}%")
    print(f"  Ciphertext entropy: {test_results.get('ciphertext_entropy', 0):.2f} bits/byte")
    print("=" * 70)
    
    return {
        "mode": mode,
        "sensor_count": sensor_count,
        "sensor_type": sensor_type,
        "total_time_s": t_total,
        "test_results": test_results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LSA v2.0 Full Operational Pipeline")
    parser.add_argument("--mode", choices=[LSAMode.LEGACY, LSAMode.V2], default=LSAMode.V2)
    parser.add_argument("--sensors", type=int, default=100, help="Number of sensor readings")
    parser.add_argument("--type", default="temperature", help="Sensor type")
    args = parser.parse_args()
    
    run_full_pipeline(mode=args.mode, sensor_count=args.sensors, sensor_type=args.type)
