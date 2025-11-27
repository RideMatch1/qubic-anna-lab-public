#!/usr/bin/env python3
"""
Extract first 100 seeds and identities from comprehensive scan results.

This script extracts 100 on-chain identities and their corresponding seeds
for public documentation.
"""

import json
from pathlib import Path
from typing import List, Dict

# Paths
CHECKPOINT_FILE = Path("../../outputs/derived/onchain_validation_checkpoint.json")
OUTPUT_FILE = Path("100_SEEDS_AND_IDENTITIES.md")
OUTPUT_JSON = Path("100_seeds_and_identities.json")

def identity_to_seed(identity: str) -> str:
 """
 Convert identity to seed using formula: identity.lower()[:55]
 
 Args:
 identity: 60-character Qubic identity (uppercase)
 
 Returns:
 55-character seed (lowercase)
 """
 if len(identity) != 60:
 raise ValueError(f"Identity must be 60 characters, got {len(identity)}")
 
 # Formula: identity.lower()[:55]
 seed = identity.lower()[:55]
 
 if len(seed) != 55:
 raise ValueError(f"Seed must be 55 characters, got {len(seed)}")
 
 return seed

def extract_seeds_and_identities(checkpoint_file: Path, count: int = 100) -> List[Dict]:
 """
 Extract seeds and identities from checkpoint file.
 
 Args:
 checkpoint_file: Path to checkpoint JSON file
 count: Number of seeds/identities to extract
 
 Returns:
 List of dicts with 'seed' and 'identity' keys
 """
 if not checkpoint_file.exists():
 raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_file}")
 
 with checkpoint_file.open() as f:
 data = json.load(f)
 
 # Get on-chain identities
 onchain_identities = data.get('onchain_identities', [])
 
 if len(onchain_identities) < count:
 print(f"Warning: Only {len(onchain_identities)} on-chain identities available, requested {count}")
 count = len(onchain_identities)
 
 results = []
 seen_seeds = set()
 
 for item in onchain_identities:
 if len(results) >= count:
 break
 
 # Extract identity
 if isinstance(item, dict):
 identity = item.get('identity', '')
 else:
 identity = str(item)
 
 if not identity or len(identity) != 60:
 continue
 
 # Convert to seed
 try:
 seed = identity_to_seed(identity)
 
 # Skip duplicates
 if seed in seen_seeds:
 continue
 
 seen_seeds.add(seed)
 results.append({
 'seed': seed,
 'identity': identity,
 'balance': item.get('balance', '0') if isinstance(item, dict) else '0',
 })
 except Exception as e:
 print(f"Error processing {identity}: {e}")
 continue
 
 return results

def write_markdown(results: List[Dict], output_file: Path) -> None:
 """Write results to Markdown file."""
 lines = [
 "# 100 Seeds and Identities - Public Documentation",
 "",
 "This document contains 100 seeds and their corresponding Qubic identities found in the Anna Matrix.",
 "",
 "## Format",
 "",
 "- **Seed**: 55-character lowercase string (derived from identity using `identity.lower()[:55]`)",
 "- **Identity**: 60-character uppercase Qubic identity (public key)",
 "- **Balance**: Current balance on-chain (as of scan date)",
 "",
 "## Important Notes",
 "",
 "- These are **public keys**, not private keys",
 "- Seeds are derived from identities using the formula: `seed = identity.lower()[:55]`",
 "- All identities exist on-chain and can be verified independently",
 "- These are the first 100 from the comprehensive scan (22,522+ on-chain identities found)",
 "",
 "## Verification",
 "",
 "You can verify these identities on-chain using:",
 "",
 "```bash",
 "docker run --rm -it -v \"$PWD\":/workspace -w /workspace qubic-proof \\",
 " python scripts/verify/rpc_check.py",
 "```",
 "",
 "Or check individually:",
 "",
 "```python",
 "from qubipy.rpc import rpc_client",
 "rpc = rpc_client.QubiPy_RPC()",
 "balance = rpc.get_balance(\"IDENTITY_HERE\")",
 "```",
 "",
 "---",
 "",
 "## Seeds and Identities",
 "",
 "| # | Seed | Identity | Balance |",
 "|---|------|----------|---------|",
 ]
 
 for idx, item in enumerate(results, 1):
 seed = item['seed']
 identity = item['identity']
 balance = item.get('balance', '0')
 lines.append(f"| {idx} | `{seed}` | `{identity}` | {balance} QU |")
 
 lines.extend([
 "",
 "---",
 "",
 "## Total",
 "",
 f"**100 seeds and identities** documented above.",
 "",
 "These are a sample from the comprehensive scan. Total on-chain identities found: 22,522+ (scan in progress).",
 "",
 "## Source",
 "",
 "Extracted from: `outputs/derived/onchain_validation_checkpoint.json`",
 "Date: 2025-11-22",
 "Scan progress: 95.9% (22,801 / 23,765 identities checked)",
 ])
 
 output_file.write_text('\n'.join(lines), encoding='utf-8')
 print(f"✓ Markdown written: {output_file}")

def write_json(results: List[Dict], output_file: Path) -> None:
 """Write results to JSON file."""
 output_data = {
 'total': len(results),
 'date': '2025-11-22',
 'source': 'onchain_validation_checkpoint.json',
 'scan_progress': '95.9% (22,801 / 23,765)',
 'seeds_and_identities': results,
 }
 
 output_file.write_text(json.dumps(output_data, indent=2), encoding='utf-8')
 print(f"✓ JSON written: {output_file}")

def main():
 """Extract and document 100 seeds and identities."""
 print("Extracting 100 seeds and identities...")
 
 # Check if checkpoint exists (might be in parent directory)
 checkpoint = CHECKPOINT_FILE
 if not checkpoint.exists():
 # Try absolute path
 checkpoint = Path(__file__).parent.parent.parent.parent / "outputs/derived/onchain_validation_checkpoint.json"
 
 if not checkpoint.exists():
 print(f"Error: Checkpoint file not found at {CHECKPOINT_FILE}")
 print(f"Tried: {checkpoint}")
 return
 
 print(f"Loading checkpoint: {checkpoint}")
 results = extract_seeds_and_identities(checkpoint, count=100)
 
 if len(results) < 100:
 print(f"Warning: Only extracted {len(results)} seeds (requested 100)")
 
 print(f"Extracted {len(results)} seeds and identities")
 
 # Write outputs
 output_dir = Path(__file__).parent.parent
 markdown_file = output_dir / OUTPUT_FILE.name
 json_file = output_dir / OUTPUT_JSON.name
 
 write_markdown(results, markdown_file)
 write_json(results, json_file)
 
 print(f"\n✓ Complete: {len(results)} seeds and identities documented")

if __name__ == "__main__":
 main()

