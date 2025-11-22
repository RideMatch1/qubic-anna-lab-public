#!/usr/bin/env python3
"""
Test all 8 extracted identities against live Qubic RPC.

Uses QubiPy library to query balances and identity info. This is the on-chain verification
step that proves the identities actually exist on the blockchain.

Usage:
    python scripts/verify/rpc_check.py
    
    Or with Docker:
    docker run --rm -v "$PWD":/workspace -w /workspace qubic-proof python scripts/verify/rpc_check.py

Outputs:
    - outputs/reports/qubipy_identity_check.json
"""

from qubipy.rpc import rpc_client
import json
from datetime import datetime
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Import identities from single source of truth
from scripts.core.identity_constants import DIAGONAL_IDENTITIES, VORTEX_IDENTITIES

# Use consistent naming
DIAGONAL_IDS = DIAGONAL_IDENTITIES
VORTEX_IDS = VORTEX_IDENTITIES

def check_identity(rpc, identity_id, label):
    """Check a single identity and return results.
    
    Queries the Qubic RPC to see if the identity exists on-chain.
    Returns status, balance, tick info, etc.
    """
    result = {
        "label": label,
        "identity": identity_id,
        "status": "unknown",
        "balance": None,
        "error": None,
    }
    
    try:
        balance_data = rpc.get_balance(identity_id)
        if balance_data:
            result["status"] = "exists"
            result["balance"] = balance_data.get("balance", "0")
            result["validForTick"] = balance_data.get("validForTick")
            result["incomingAmount"] = balance_data.get("incomingAmount", "0")
            result["outgoingAmount"] = balance_data.get("outgoingAmount", "0")
        else:
            result["status"] = "not_found"
    except Exception as e:
        # network errors, RPC issues, etc.
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 80)
    print("QUBIC IDENTITY LIVE CHECK")
    print("=" * 80)
    print()
    
    try:
        rpc = rpc_client.QubiPy_RPC()
        latest_tick = rpc.get_latest_tick()
        print(f"Connected to Qubic RPC. Latest tick: {latest_tick}")
        print()
    except Exception as e:
        print(f"ERROR: Failed to connect to RPC: {e}")
        return
    
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "latest_tick": latest_tick,
        "diagonal_identities": [],
        "vortex_identities": [],
    }
    
    print("=" * 80)
    print("DIAGONAL IDENTITIES (4)")
    print("=" * 80)
    print()
    
    for idx, identity_id in enumerate(DIAGONAL_IDS, 1):
        label = f"Diagonal #{idx}"
        print(f"Checking {label}...")
        result = check_identity(rpc, identity_id, label)
        results["diagonal_identities"].append(result)
        
        if result["status"] == "exists":
            print(f"  ✓ EXISTS - Balance: {result['balance']} QU")
            print(f"    Valid for tick: {result.get('validForTick', 'N/A')}")
        elif result["status"] == "not_found":
            print(f"  ✗ NOT FOUND - Identity not on blockchain")
        else:
            print(f"  ✗ ERROR - {result.get('error', 'Unknown error')}")
        print()
    
    print("=" * 80)
    print("VORTEX IDENTITIES (4)")
    print("=" * 80)
    print()
    
    for idx, identity_id in enumerate(VORTEX_IDS, 1):
        label = f"Vortex #{idx}"
        print(f"Checking {label}...")
        result = check_identity(rpc, identity_id, label)
        results["vortex_identities"].append(result)
        
        if result["status"] == "exists":
            print(f"  ✓ EXISTS - Balance: {result['balance']} QU")
            print(f"    Valid for tick: {result.get('validForTick', 'N/A')}")
        elif result["status"] == "not_found":
            print(f"  ✗ NOT FOUND - Identity not on blockchain")
        else:
            print(f"  ✗ ERROR - {result.get('error', 'Unknown error')}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    total = len(DIAGONAL_IDS) + len(VORTEX_IDS)
    exists = sum(1 for r in results["diagonal_identities"] + results["vortex_identities"] if r["status"] == "exists")
    not_found = sum(1 for r in results["diagonal_identities"] + results["vortex_identities"] if r["status"] == "not_found")
    errors = sum(1 for r in results["diagonal_identities"] + results["vortex_identities"] if r["status"] == "error")
    
    print(f"Total identities checked: {total}")
    print(f"  Exists on blockchain: {exists}")
    print(f"  Not found: {not_found}")
    print(f"  Errors: {errors}")
    print()
    
    # Save JSON results
    output_file = "outputs/reports/qubipy_identity_check.json"
    try:
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")
        # Don't fail the whole script if we can't write the file
    
    print()
    print("=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

