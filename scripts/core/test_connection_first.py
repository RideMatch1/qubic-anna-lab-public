#!/usr/bin/env python3
"""
Connection Test - Teste zuerst alle Verbindungen
Bevor wir die eigentlichen Tests machen
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("CONNECTION TEST - Schritt for Schritt")
print("=" * 80)
print()

# Test 1: Docker
print("1. Testing Docker...")
try:
 result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
 if result.returncode == 0:
 print(f" ✅ Docker available: {result.stdout.strip()}")
 else:
 print(" ❌ Docker not working")
 sys.exit(1)
except FileNotFoundError:
 print(" ❌ Docker not found")
 sys.exit(1)
except Exception as e:
 print(f" ❌ Docker error: {e}")
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
 print(f" ❌ Docker Python failed: {result.stderr}")
 sys.exit(1)
except subprocess.TimeoutExpired:
 print(" ❌ Docker timeout")
 sys.exit(1)
except Exception as e:
 print(f" ❌ Docker error: {e}")
 sys.exit(1)

print()

# Test 3: QubiPy in Docker
print("3. Testing QubiPy in Docker...")
script = '''
import sys
try:
 from qubipy.crypto.utils import get_subseed_from_seed
 print("OK")
except ImportError as e:
 print("IMPORT_ERROR: " + str(e))
 sys.exit(1)
'''
try:
 result = subprocess.run(
 ['docker', 'run', '--rm', 'python:3.11', 'bash', '-c', 
 f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=120
 )
 if result.returncode == 0 and "OK" in result.stdout:
 print(" ✅ QubiPy installs and imports in Docker")
 else:
 print(f" ❌ QubiPy failed: {result.stderr}")
 sys.exit(1)
except subprocess.TimeoutExpired:
 print(" ❌ Docker timeout (QubiPy installation takes time)")
 sys.exit(1)
except Exception as e:
 print(f" ❌ Error: {e}")
 sys.exit(1)

print()

# Test 4: Identity Derivation in Docker
print("4. Testing Identity Derivation in Docker...")
script = '''
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
seed = "a" * 55
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=120
 )
 if result.returncode == 0 and len(result.stdout.strip()) == 60:
 identity = result.stdout.strip()
 print(f" ✅ Identity derivation works!")
 print(f" Test identity: {identity[:40]}...")
 else:
 print(f" ❌ Derivation failed: {result.stderr}")
 sys.exit(1)
except subprocess.TimeoutExpired:
 print(" ❌ Docker timeout")
 sys.exit(1)
except Exception as e:
 print(f" ❌ Error: {e}")
 sys.exit(1)

print()

# Test 5: RPC Connection in Docker
print("5. Testing RPC Connection in Docker...")
script = '''
from qubipy.rpc import rpc_client
try:
 rpc = rpc_client.QubiPy_RPC()
 tick = rpc.get_latest_tick()
 print("OK|" + str(tick))
except Exception as e:
 print("ERROR|" + str(e))
'''
try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=60
 )
 if result.returncode == 0 and "OK|" in result.stdout:
 parts = result.stdout.strip().split("|")
 tick = parts[1] if len(parts) > 1 else "N/A"
 print(f" ✅ RPC connection works!")
 print(f" Latest tick: {tick}")
 else:
 error = result.stdout.strip().split("|")[1] if "ERROR|" in result.stdout else result.stderr
 print(f" ⚠️ RPC connection failed: {error}")
 print(" (Das ist OK, wir können trotzdem Seeds testen)")
except subprocess.TimeoutExpired:
 print(" ⚠️ RPC timeout (kann normal sein)")
except Exception as e:
 print(f" ⚠️ RPC error: {e}")

print()
print("=" * 80)
print("CONNECTION TEST COMPLETE")
print("=" * 80)
print()
print("✅ Alle Basis-Verbindungen getestet!")
print(" Jetzt können wir die eigentlichen Tests ausführen.")
print()

