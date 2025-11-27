#!/usr/bin/env python3
"""
Simple Connection Test - Ohne f-strings in Scripts
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("CONNECTION TEST - Simplified")
print("=" * 80)
print()

# Test 1: Docker
print("1. Testing Docker...")
try:
 result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
 if result.returncode == 0:
 print(" ✅ Docker available")
 else:
 print(" ❌ Docker not working")
 sys.exit(1)
except FileNotFoundError:
 print(" ❌ Docker not found")
 sys.exit(1)

print()

# Test 2: Docker Python
print("2. Testing Docker Python...")
try:
 result = subprocess.run(
 ['docker', 'run', '--rm', 'python:3.11', 'python3', '-c', 'print("OK")'],
 capture_output=True,
 text=True,
 timeout=30
 )
 if result.returncode == 0:
 print(" ✅ Docker Python works")
 else:
 print(" ❌ Docker Python failed")
 sys.exit(1)
except Exception as e:
 print(" ❌ Docker error: " + str(e))
 sys.exit(1)

print()

# Test 3: QubiPy Installation
print("3. Testing QubiPy installation in Docker...")
print(" (This may take a minute...)")
sys.stdout.flush()

try:
 result = subprocess.run(
 ['docker', 'run', '--rm', 'python:3.11', 'bash', '-c', 
 'pip install -q qubipy > /dev/null 2>&1 && python3 -c "from qubipy.crypto.utils import get_subseed_from_seed; print(\"OK\")"'],
 capture_output=True,
 text=True,
 timeout=180
 )
 if result.returncode == 0 and "OK" in result.stdout:
 print(" ✅ QubiPy installs and imports")
 else:
 print(" ❌ QubiPy failed")
 print(" Error: " + result.stderr[:200])
 sys.exit(1)
except subprocess.TimeoutExpired:
 print(" ❌ Docker timeout (QubiPy installation takes time)")
 sys.exit(1)
except Exception as e:
 print(" ❌ Error: " + str(e))
 sys.exit(1)

print()

# Test 4: Identity Derivation
print("4. Testing Identity Derivation...")
sys.stdout.flush()

script_content = "from qubipy.crypto.utils import get_subseed_from_seed, get_private_key_from_subseed, get_public_key_from_private_key, get_identity_from_public_key; seed = 'a' * 55; seed_bytes = seed.encode('utf-8'); subseed = get_subseed_from_seed(seed_bytes); private_key = get_private_key_from_subseed(subseed); public_key = get_public_key_from_private_key(private_key); identity = get_identity_from_public_key(public_key); print(identity)"

try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', str(project_root) + ':/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', 
 'pip install -q qubipy > /dev/null 2>&1 && python3 -c "' + script_content + '"'],
 capture_output=True,
 text=True,
 timeout=120
 )
 if result.returncode == 0 and len(result.stdout.strip()) == 60:
 identity = result.stdout.strip()
 print(" ✅ Identity derivation works!")
 print(" Test identity: " + identity[:40] + "...")
 else:
 print(" ❌ Derivation failed")
 print(" Error: " + result.stderr[:200])
 sys.exit(1)
except subprocess.TimeoutExpired:
 print(" ❌ Docker timeout")
 sys.exit(1)
except Exception as e:
 print(" ❌ Error: " + str(e))
 sys.exit(1)

print()

# Test 5: RPC (optional)
print("5. Testing RPC Connection (optional)...")
sys.stdout.flush()

rpc_script = "from qubipy.rpc import rpc_client; rpc = rpc_client.QubiPy_RPC(); tick = rpc.get_latest_tick(); print('OK|' + str(tick))"

try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', str(project_root) + ':/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', 
 'pip install -q qubipy > /dev/null 2>&1 && python3 -c "' + rpc_script + '"'],
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
 error = result.stderr[:200] if result.stderr else result.stdout[:200]
 print(" ⚠️ RPC connection failed (this is OK)")
 print(" Error: " + error)
except subprocess.TimeoutExpired:
 print(" ⚠️ RPC timeout (this is OK)")
except Exception as e:
 print(" ⚠️ RPC error (this is OK): " + str(e))

print()
print("=" * 80)
print("CONNECTION TEST COMPLETE")
print("=" * 80)
print()
print("✅ All basic connections tested!")
print(" Now you can run the validation scripts.")
print()

