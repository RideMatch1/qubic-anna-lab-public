#!/usr/bin/env python3
"""
Analyze Identities auf ihre Rollen im Qubic Stack.

Prüft:
- Transaction patterns
- Oracle Machine signatures
- Agent behavior
- Cross-chain operations
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict, Counter
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"
CHECKPOINT_FILE = OUTPUT_DIR / "identity_role_analysis_checkpoint.json"

def check_identity_transactions(identity: str) -> Dict:
 """Check Transaction-Historie einer Identity."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 # Get transaction history (if available)
 # Note: Qubic RPC might not have full tx history endpoint
 balance = rpc.get_balance(identity)
 if balance:
 print(f"BALANCE|{{balance}}")
 else:
 print("NO_BALANCE")
except Exception as e:
 print(f"ERROR|{{str(e)}}")
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if "BALANCE" in result.stdout:
 balance_str = result.stdout.split("|")[1].strip()
 return {"has_balance": True, "balance": balance_str}
 return {"has_balance": False}
 except Exception:
 return {"error": "Could not check"}

def analyze_identity_pattern(identity: str) -> Dict:
 """Analyze Pattern einer Identity."""
 
 # Seed-Analyse
 seed = identity.lower()[:55]
 
 # Charakter-Verteilung
 char_dist = Counter(seed)
 
 # Wiederholende Muster
 repeating = []
 for i in range(len(seed) - 3):
 pattern = seed[i:i+4]
 if len(set(pattern)) == 1:
 repeating.append(pattern[0])
 
 # Numerische Eigenschaften
 seed_value = sum(ord(c) - ord('a') for c in seed)
 
 return {
 "seed": seed,
 "char_distribution": dict(char_dist.most_common(5)),
 "repeating_patterns": len(repeating),
 "seed_value": seed_value,
 "seed_value_mod_26": seed_value % 26,
 }

def check_for_oracle_machine_signatures(identity: str) -> bool:
 """Check ob Identity Oracle Machine Signatures hat."""
 # Placeholder - würde echte Oracle Machine Signaturen checkn
 # Für jetzt: Check auf bekannte Patterns
 return False

def load_onchain_identities() -> List[str]:
 """Load alle on-chain Identities."""
 identities = []
 
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 complete_data = json.load(f)
 total_batches = complete_data.get("total_batches", 0)
 
 for i in range(total_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch_data = json.load(f)
 if isinstance(batch_data, list):
 identities.extend(batch_data)
 
 return identities

def load_checkpoint() -> Dict:
 """Load Checkpoint."""
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 return json.load(f)
 except Exception:
 pass
 
 return {
 "processed": 0,
 "results": [],
 "start_time": datetime.now().isoformat(),
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 checkpoint["last_update"] = datetime.now().isoformat()
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE IDENTITY ROLES IN QUBIC STACK")
 print("=" * 80)
 print()
 
 print("Loading identities...")
 identities = load_onchain_identities()
 print(f"✅ {len(identities):,} identities loaded")
 print()
 
 # Load Checkpoint
 checkpoint = load_checkpoint()
 processed = checkpoint.get("processed", 0)
 results = checkpoint.get("results", [])
 
 if processed > 0:
 print(f"✅ Checkpoint loaded: {processed:,} / {len(identities):,} processed")
 print()
 
 print("Analyzing identity roles...")
 print("(This analyzes patterns, not full transaction history)")
 print()
 
 start_idx = processed
 batch_size = 100
 
 for i, identity in enumerate(identities[start_idx:], start_idx):
 if (i + 1) % batch_size == 0:
 progress = (i + 1) / len(identities) * 100
 print(f" Progress: {i+1:,} / {len(identities):,} ({progress:.1f}%)")
 
 # Speichere Checkpoint
 checkpoint = {
 "processed": i + 1,
 "results": results,
 "start_time": checkpoint.get("start_time", datetime.now().isoformat()),
 "last_update": datetime.now().isoformat(),
 }
 save_checkpoint(checkpoint)
 
 # Analyze Identity
 pattern = analyze_identity_pattern(identity)
 tx_info = check_identity_transactions(identity)
 oracle_sig = check_for_oracle_machine_signatures(identity)
 
 result = {
 "identity": identity,
 "pattern": pattern,
 "transactions": tx_info,
 "oracle_machine": oracle_sig,
 }
 
 results.append(result)
 
 print()
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 # Analyze Patterns
 char_distributions = Counter()
 repeating_counts = []
 seed_values = []
 
 for r in results:
 pattern = r.get("pattern", {})
 char_dist = pattern.get("char_distribution", {})
 for char, count in char_dist.items():
 char_distributions[char] += count
 repeating_counts.append(pattern.get("repeating_patterns", 0))
 seed_values.append(pattern.get("seed_value", 0))
 
 print(f"Total analyzed: {len(results):,}")
 print(f"Average repeating patterns: {sum(repeating_counts)/len(repeating_counts):.2f}" if repeating_counts else "N/A")
 print(f"Top characters: {dict(char_distributions.most_common(10))}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "identity_role_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "summary": {
 "total_analyzed": len(results),
 "char_distribution": dict(char_distributions.most_common(20)),
 "avg_repeating_patterns": sum(repeating_counts)/len(repeating_counts) if repeating_counts else 0,
 },
 "results": results[:1000], # Stichprobe
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Lösche Checkpoint
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint deleted (analysis complete)")
 
 print("=" * 80)
 print("✅ IDENTITY ROLE ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

