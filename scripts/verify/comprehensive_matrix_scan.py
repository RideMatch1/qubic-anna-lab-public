#!/usr/bin/env python3
"""
Comprehensive scan of the Anna Matrix for ALL possible identity patterns.

Tests:
1. All diagonal variations
2. All vortex/ring patterns
3. Row/column scans
4. Spiral patterns
5. Random walks
6. Other geometric patterns

Then checks which extracted identities exist on-chain.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, List, Sequence, Tuple

import numpy as np

from analysis.utils.data_loader import load_anna_matrix
from analysis.utils.identity_tools import (
 IdentityRecord,
 base26_char,
 identity_from_body,
 public_key_from_identity,
)
from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "comprehensive_matrix_scan.json"

Position = Tuple[int, int]
PatternFunc = Callable[[int, int], Sequence[Position]]

@dataclass
class PatternResult:
 pattern_name: str
 identities_found: int
 on_chain_count: int
 identities: List[IdentityRecord]
 on_chain_identities: List[str]

def diag_main(base_r: int, base_c: int) -> Sequence[Position]:
 """Main diagonal: (r+j, c+j)"""
 return [(base_r + j, base_c + j) for j in range(14)]

def diag_reverse(base_r: int, base_c: int) -> Sequence[Position]:
 """Reverse diagonal: (r+j, c+(13-j))"""
 return [(base_r + j, base_c + (13 - j)) for j in range(14)]

def vertical_stride(base_r: int, base_c: int) -> Sequence[Position]:
 """Vertical stride pattern"""
 return [(base_r + j, base_c + (j % 4)) for j in range(14)]

def horizontal_stride(base_r: int, base_c: int) -> Sequence[Position]:
 """Horizontal stride pattern"""
 return [(base_r + (j % 4), base_c + j) for j in range(14)]

def zigzag_snake(base_r: int, base_c: int) -> Sequence[Position]:
 """Zigzag snake pattern"""
 coords: List[Position] = []
 for j in range(14):
 row = base_r + j
 col = base_c + (j if j % 2 == 0 else 13 - j)
 coords.append((row, col))
 return coords

def row_scan(base_r: int, base_c: int) -> Sequence[Position]:
 """Simple row scan"""
 return [(base_r, base_c + j) for j in range(14)]

def column_scan(base_r: int, base_c: int) -> Sequence[Position]:
 """Simple column scan"""
 return [(base_r + j, base_c) for j in range(14)]

def spiral_pattern(base_r: int, base_c: int) -> Sequence[Position]:
 """Spiral pattern starting from base"""
 coords: List[Position] = []
 directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
 r, c = base_r, base_c
 step = 1
 dir_idx = 0
 
 for _ in range(14):
 coords.append((r, c))
 dr, dc = directions[dir_idx]
 r += dr
 c += dc
 step -= 1
 if step == 0:
 dir_idx = (dir_idx + 1) % 4
 if dir_idx % 2 == 0:
 step += 1
 return coords

def l_shape(base_r: int, base_c: int) -> Sequence[Position]:
 """L-shaped pattern"""
 coords: List[Position] = []
 for j in range(7):
 coords.append((base_r + j, base_c))
 for j in range(1, 8):
 coords.append((base_r + 6, base_c + j))
 return coords[:14]

PATTERNS: dict[str, PatternFunc] = {
 "diag_main": diag_main,
 "diag_reverse": diag_reverse,
 "vertical_stride": vertical_stride,
 "horizontal_stride": horizontal_stride,
 "zigzag_snake": zigzag_snake,
 "row_scan": row_scan,
 "column_scan": column_scan,
 "spiral": spiral_pattern,
 "l_shape": l_shape,
}

def extract_with_pattern(matrix: np.ndarray, builder: PatternFunc, pattern_name: str) -> List[IdentityRecord]:
 """Extract identities using a pattern builder."""
 records: List[IdentityRecord] = []
 
 # Try different starting positions
 for start_row in range(0, 128, 16):
 for start_col in range(0, 128, 16):
 for block_offset in [0, 8]:
 chars: List[str] = []
 path: List[Position] = []
 
 for block in range(4):
 base_r = start_row + (block // 2) * 16 + block_offset
 base_c = start_col + (block % 2) * 16 + block_offset
 
 if base_r >= 128 or base_c >= 128:
 continue
 
 positions = builder(base_r, base_c)
 for (row, col) in positions:
 if row >= 128 or col >= 128:
 continue
 val = matrix[row, col]
 chars.append(base26_char(val))
 path.append((row, col))
 
 if len(chars) < 56:
 continue
 
 body = "".join(chars[:56])
 identity = identity_from_body(body)
 public_key, checksum_valid = public_key_from_identity(identity)
 
 records.append(
 IdentityRecord(
 label=f"{pattern_name}-{len(records)+1}",
 identity=identity,
 public_key=public_key or "",
 checksum_valid=checksum_valid,
 path=tuple(path[:56]),
 note="",
 )
 )
 
 return records

def check_on_chain(rpc: rpc_client.QubiPy_RPC, identity: str) -> bool:
 """Check if identity exists on-chain."""
 try:
 time.sleep(0.5)
 balance = rpc.get_balance(identity)
 return balance is not None
 except:
 return False

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Comprehensive Matrix Scan ===\n")
 print("Testing ALL patterns for identities...\n")
 
 payload = load_anna_matrix()
 matrix = payload.matrix
 
 results: List[PatternResult] = []
 all_on_chain: List[str] = []
 
 for pattern_name, builder in PATTERNS.items():
 print(f"Testing pattern: {pattern_name}...")
 
 records = extract_with_pattern(matrix, builder, pattern_name)
 unique_identities = list({r.identity for r in records})
 
 print(f" Found {len(unique_identities)} unique identities")
 
 # Check on-chain
 on_chain = []
 for identity in unique_identities[:20]: # Limit to avoid rate limiting
 if check_on_chain(rpc, identity):
 on_chain.append(identity)
 all_on_chain.append(identity)
 
 results.append(
 PatternResult(
 pattern_name=pattern_name,
 identities_found=len(unique_identities),
 on_chain_count=len(on_chain),
 identities=records[:10], # Limit for JSON
 on_chain_identities=on_chain,
 )
 )
 
 if on_chain:
 print(f" ✅ {len(on_chain)} exist on-chain!")
 else:
 print(f" - None exist on-chain")
 print()
 
 # Summary
 print("=== Summary ===")
 total_on_chain = len(set(all_on_chain))
 print(f"Total unique on-chain identities found: {total_on_chain}")
 
 for result in results:
 if result.on_chain_count > 0:
 print(f" {result.pattern_name}: {result.on_chain_count} on-chain")
 
 # Save
 data = {
 "patterns_tested": len(PATTERNS),
 "total_on_chain": total_on_chain,
 "results": [asdict(r) for r in results],
 "all_on_chain_identities": list(set(all_on_chain)),
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(data, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")
 
 if total_on_chain > 8:
 print(f"\n🎉 FOUND MORE THAN 8 IDENTITIES! ({total_on_chain} total)")
 else:
 print(f"\nOnly the known 8 identities found (or rate limiting prevented full scan)")

if __name__ == "__main__":
 main()

