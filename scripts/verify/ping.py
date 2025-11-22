#!/usr/bin/env python3
"""
Quick connectivity test for Qubic RPC.

Just checks if we can connect and get the latest tick. Useful for debugging
connection issues before running the full verification scripts.

Usage:
    python scripts/verify/ping.py
    
    Or with Docker:
    docker run --rm -v "$PWD":/workspace -w /workspace qubic-proof python scripts/verify/ping.py
"""

from qubipy.rpc import rpc_client

def main():
    try:
        rpc = rpc_client.QubiPy_RPC()
        latest_tick = rpc.get_latest_tick()
        print(f"✓ Connected to Qubic RPC")
        print(f"  Latest tick: {latest_tick}")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
