#!/usr/bin/env python3
"""
Exhaustive search: Try EVERY possible 56-character window in the Base-26 matrix
and check which ones produce valid Qubic identities that exist on-chain.

This is the most comprehensive search possible.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Set

import numpy as np

from analysis.utils.data_loader import load_anna_matrix
from analysis.utils.identity_tools import (
 base26_char,
 identity_from_body,
 public_key_from_identity,
)
from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "exhaustive_matrix_search.json"

KNOWN_8 = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def check_on_chain(rpc: rpc_client.QubiPy_RPC, identity: str) -> bool:
 """Quick on-chain check."""
 try:
 time.sleep(0.3)
 balance = rpc.get_balance(identity)
 return balance is not None
 except:
 return False

def extract_all_windows(matrix: np.ndarray) -> Set[str]:
 """Extract all possible 56-character windows from the matrix."""
 identities: Set[str] = set()
 size = matrix.shape[0]
 
 # Convert to Base-26 string
 base26_str = ""
 for r in range(size):
 for c in range(size):
 base26_str += base26_char(matrix[r, c])
 
 print(f"Matrix converted to Base-26 string: {len(base26_str)} characters")
 print(f"Total possible 56-char windows: {len(base26_str) - 55}")
 
 # Extract all 56-char windows
 checked = 0
 for i in range(len(base26_str) - 55):
 window = base26_str[i:i+56]
 identity = identity_from_body(window)
 pk, checksum_valid = public_key_from_identity(identity)
 
 if checksum_valid:
 identities.add(identity)
 
 checked += 1
 if checked % 10000 == 0:
 print(f" Checked {checked} windows, found {len(identities)} valid identities...")
 
 return identities

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Exhaustive Matrix Search ===\n")
 print("This will check EVERY possible 56-character window in the matrix.\n")
 
 payload = load_anna_matrix()
 matrix = payload.matrix
 
 print("Step 1: Extracting all valid identities from matrix...")
 all_identities = extract_all_windows(matrix)
 
 print(f"\nStep 2: Found {len(all_identities)} unique valid identities")
 print(f"Checking which ones exist on-chain...\n")
 
 on_chain: List[str] = []
 for i, identity in enumerate(all_identities, 1):
 if i % 100 == 0:
 print(f" Checked {i}/{len(all_identities)}, found {len(on_chain)} on-chain...")
 
 if check_on_chain(rpc, identity):
 on_chain.append(identity)
 if identity not in KNOWN_8:
 print(f" 🎉 NEW on-chain identity: {identity}")
 
 new_ones = [id for id in on_chain if id not in KNOWN_8]
 
 print(f"\n=== Results ===")
 print(f"Total valid identities from matrix: {len(all_identities)}")
 print(f"On-chain identities: {len(on_chain)}")
 print(f"Known 8: {len([id for id in on_chain if id in KNOWN_8])}")
 print(f"NEW on-chain identities: {len(new_ones)}")
 
 if new_ones:
 print(f"\n🎉 FOUND {len(new_ones)} NEW ON-CHAIN IDENTITIES!")
 print(f"\nFirst 20 new identities:")
 for i, identity in enumerate(new_ones[:20], 1):
 print(f" {i}. {identity}")
 
 # Save
 output = {
 "total_valid_identities": len(all_identities),
 "on_chain_count": len(on_chain),
 "known_8_count": len([id for id in on_chain if id in KNOWN_8]),
 "new_on_chain_count": len(new_ones),
 "all_on_chain": on_chain,
 "new_identities": new_ones,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

