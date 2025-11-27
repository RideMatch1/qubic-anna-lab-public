#!/usr/bin/env python3
"""
Direct Test - Gemini Approach
Testet direkt ohne Abhängigkeiten
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("GEMINI DIRECT TEST")
print("=" * 80)
print()

# Load fast test data (or create it)
fast_file = project_root / "outputs" / "derived" / "gemini_raw_value_test_fast.json"
existing_file = project_root / "outputs" / "derived" / "gemini_raw_value_test.json"

if not fast_file.exists() and existing_file.exists():
 print("Creating fast test file from existing data...")
 with existing_file.open() as f:
 data = json.load(f)
 
 # Create fast test format
 fast_data = {
 "documented_identity": data.get("documented_identity", ""),
 "documented_seed": data.get("documented_seed", ""),
 "raw_values_sample": data.get("raw_values_sample", []),
 "results": [
 {
 "method": "Raw (Absolute) % 26",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "match_with_documented_seed": False
 }
 ]
 }
 
 fast_file.parent.mkdir(parents=True, exist_ok=True)
 with fast_file.open("w") as f:
 json.dump(fast_data, f, indent=2)
 print(f"✅ Created {fast_file}")
 print()

# Load test data
if not fast_file.exists():
 print("❌ Fast test file not found!")
 sys.exit(1)

with fast_file.open() as f:
 data = json.load(f)

documented_identity = data.get("documented_identity", "")
documented_seed = data.get("documented_seed", "")
results = data.get("results", [])

print(f"Target Identity: {documented_identity[:40]}...")
print(f"Documented Seed: {documented_seed[:40]}...")
print(f"Test Results: {len(results)}")
print()

# Test identity derivation
print("Testing identity derivation methods...")
print()

# Method 1: Try local QubiPy
print("1. Testing local QubiPy...")
try:
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 )
 
 test_seed = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 seed_bytes = test_seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 
 print(f" ✅ Local QubiPy works!")
 print(f" Test seed: {test_seed[:40]}...")
 print(f" Derived identity: {identity[:40]}...")
 print(f" Match with target: {'✅ YES!' if identity == documented_identity else '❌ NO'}")
 print()
 
 # Test on-chain check
 print("2. Testing on-chain check...")
 try:
 from qubipy.rpc import rpc_client
 rpc = rpc_client.QubiPy_RPC()
 balance_data = rpc.get_balance(identity)
 
 if balance_data:
 print(f" ✅ Identity exists on-chain!")
 print(f" Balance: {balance_data.get('balance', 'N/A')}")
 else:
 print(f" ❌ Identity not found on-chain")
 except Exception as e:
 print(f" ⚠️ RPC check failed: {e}")
 
 print()
 
except ImportError:
 print(" ❌ QubiPy not available locally")
 print()
 print(" Trying direct TCP RPC...")
 
 # Test direct TCP RPC
 import socket
 test_identity = documented_identity
 
 payload = {
 "jsonrpc": "2.0",
 "id": 1,
 "method": "getIdentity",
 "params": {"identity": test_identity},
 }
 
 nodes = [
 ("167.99.139.198", 21841),
 ("167.99.253.63", 21841),
 ("134.122.69.166", 21841),
 ]
 
 for host, port in nodes:
 try:
 data = json.dumps(payload).encode("utf-8") + b"\n"
 with socket.create_connection((host, port), timeout=5.0) as sock:
 sock.sendall(data)
 raw = sock.makefile().readline()
 resp = json.loads(raw)
 
 if "result" in resp:
 print(f" ✅ TCP RPC works! (Node: {host}:{port})")
 print(f" Response: {resp.get('result', {})}")
 break
 except Exception as e:
 print(f" ⚠️ Node {host}:{port} failed: {e}")
 continue
 else:
 print(" ❌ All TCP RPC nodes failed")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

