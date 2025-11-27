#!/usr/bin/env python3
"""
Test with Existing Docker Image
Nutzt das bereits gebaute qubic-proof Image
"""

import sys
import subprocess
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("TEST WITH EXISTING DOCKER IMAGE")
print("=" * 80)
print()

# Check if image exists
print("1. Checking for qubic-proof image...")
result = subprocess.run(
 ['docker', 'images', 'qubic-proof'],
 capture_output=True,
 text=True
)

if 'qubic-proof' not in result.stdout:
 print(" ⚠️ qubic-proof image not found")
 print(" Building it now...")
 sys.stdout.flush()
 
 build_result = subprocess.run(
 ['docker', 'build', '-f', 'github_export/Dockerfile.qubipy', '-t', 'qubic-proof', '.'],
 capture_output=True,
 text=True,
 timeout=300
 )
 
 if build_result.returncode != 0:
 print(" ❌ Build failed")
 print(" Error: " + build_result.stderr[:500])
 sys.exit(1)
 
 print(" ✅ Image built successfully")
else:
 print(" ✅ qubic-proof image exists")

print()

# Test QubiPy in image
print("2. Testing QubiPy in qubic-proof image...")
script = "from qubipy.crypto.utils import get_subseed_from_seed, get_private_key_from_subseed, get_public_key_from_private_key, get_identity_from_public_key; seed = 'a' * 55; seed_bytes = seed.encode('utf-8'); subseed = get_subseed_from_seed(seed_bytes); private_key = get_private_key_from_subseed(subseed); public_key = get_public_key_from_private_key(private_key); identity = get_identity_from_public_key(public_key); print(identity)"

try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', str(project_root) + ':/workspace', '-w', '/workspace',
 'qubic-proof', 'python3', '-c', script],
 capture_output=True,
 text=True,
 timeout=60
 )
 
 if result.returncode == 0 and len(result.stdout.strip()) == 60:
 identity = result.stdout.strip()
 print(" ✅ QubiPy works in qubic-proof image!")
 print(" Test identity: " + identity[:40] + "...")
 else:
 print(" ❌ QubiPy failed")
 print(" Error: " + result.stderr[:500])
 sys.exit(1)
except Exception as e:
 print(" ❌ Error: " + str(e))
 sys.exit(1)

print()

# Test RPC
print("3. Testing RPC connection...")
rpc_script = "from qubipy.rpc import rpc_client; rpc = rpc_client.QubiPy_RPC(); tick = rpc.get_latest_tick(); print('OK|' + str(tick))"

try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', str(project_root) + ':/workspace', '-w', '/workspace',
 'qubic-proof', 'python3', '-c', rpc_script],
 capture_output=True,
 text=True,
 timeout=60
 )
 
 if result.returncode == 0 and "OK|" in result.stdout:
 parts = result.stdout.strip().split("|")
 tick = parts[1] if len(parts) > 1 else "N/A"
 print(" ✅ RPC connection works!")
 print(" Latest tick: " + str(tick))
 else:
 print(" ⚠️ RPC connection failed (this is OK)")
 print(" Error: " + (result.stderr[:200] if result.stderr else result.stdout[:200]))
except Exception as e:
 print(" ⚠️ RPC error (this is OK): " + str(e))

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()
print("✅ qubic-proof image is ready!")
print(" You can now use it for validation:")
print(" python3 scripts/core/validate_seeds_docker_final.py")
print()

