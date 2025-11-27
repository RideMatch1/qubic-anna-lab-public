#!/usr/bin/env python3
"""
Position 30 + Position 4 Combination - Live RPC Validation

Testet die Kombination mit ECHTEN LIVE RPC-CALLS:
- 500 Layer-3 Identities ableiten
- Für jede Identity ECHTEN RPC-Call machen
- Position 30 + Position 4 analyzen
- Kombination testen
- Vollständige Validierung
"""

import json
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
ANALYSIS_DIR = project_root / "outputs" / "analysis"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> str:
 """Leite Identity aus Seed ab (via venv-tx)."""
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
try:
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 print(identity)
except Exception as e:
 print(f"ERROR: {{e}}")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 if result.returncode == 0 and result.stdout.strip() and not result.stdout.startswith("ERROR"):
 return result.stdout.strip()
 except Exception:
 pass
 return ""

def check_identity_onchain_live(identity: str) -> bool:
 """Check ob Identity on-chain existiert - ECHTER LIVE RPC-CALL."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print("EXISTS")
 else:
 print("NOT_FOUND")
except Exception as e:
 print(f"ERROR: {{e}}")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 return "EXISTS" in result.stdout
 except Exception:
 return False

def load_layer1_identities(count: int = 500) -> List[str]:
 """Load Layer-1 Identities aus complete_mapping_database.json."""
 mapping_file = ANALYSIS_DIR / "complete_mapping_database.json"
 
 if not mapping_file.exists():
 print(f"❌ Mapping database not found: {mapping_file}")
 return []
 
 print(f"Loading {count} Layer-1 identities from mapping database...")
 with mapping_file.open() as f:
 data = json.load(f)
 
 # Datenstruktur: {"seed_to_real_id": {...}}
 if isinstance(data, dict) and "seed_to_real_id" in data:
 identities = list(data["seed_to_real_id"].values())[:count]
 return identities
 
 return []

def derive_layer3_from_layer1(layer1_identity: str) -> Tuple[str, str, str]:
 """Leite Layer-3 von Layer-1 ab."""
 # Layer-1 → Layer-2
 layer2_seed = identity_to_seed(layer1_identity)
 layer2_identity = derive_identity_from_seed(layer2_seed)
 
 if not layer2_identity:
 return "", "", ""
 
 # Layer-2 → Layer-3
 layer3_seed = identity_to_seed(layer2_identity)
 layer3_identity = derive_identity_from_seed(layer3_seed)
 
 return layer2_identity, layer3_identity, layer3_seed

def test_combination_live(count: int = 500) -> Dict:
 """Teste Kombination mit ECHTEN LIVE RPC-CALLS."""
 print("=" * 80)
 print("POSITION 30 + POSITION 4 COMBINATION - LIVE RPC VALIDATION")
 print("=" * 80)
 print()
 print(f"⚠️ WARNING: This will make {count} REAL RPC calls!")
 print(f" Estimated time: {count * 2 / 60:.1f} minutes")
 print()
 
 # Load Layer-1 Identities
 layer1_identities = load_layer1_identities(count)
 
 if not layer1_identities:
 return {"error": "No identities loaded"}
 
 print(f"✅ Loaded {len(layer1_identities)} Layer-1 identities")
 print()
 
 # Sammle Daten
 results = []
 pos30_onchain = Counter()
 pos30_offchain = Counter()
 pos4_onchain = Counter()
 pos4_offchain = Counter()
 combo_onchain = defaultdict(int)
 combo_offchain = defaultdict(int)
 
 print("Deriving Layer-3 and checking on-chain status...")
 print("This will take a while...")
 print()
 
 # Progress file
 progress_file = OUTPUT_DIR / "live_rpc_progress.json"
 
 start_time = time.time()
 
 for i, layer1_id in enumerate(layer1_identities, 1):
 # Leite Layer-3 ab
 layer2_id, layer3_id, layer3_seed = derive_layer3_from_layer1(layer1_id)
 
 if not layer3_id or len(layer3_id) < 60:
 continue
 
 # ECHTER LIVE RPC-CALL
 is_onchain = check_identity_onchain_live(layer3_id)
 
 # Position 30 und Position 4
 pos30_char = layer3_id[30]
 pos4_char = layer3_id[4]
 combo_key = f"{pos4_char}{pos30_char}"
 
 # Sammle Daten
 if is_onchain:
 pos30_onchain[pos30_char] += 1
 pos4_onchain[pos4_char] += 1
 combo_onchain[combo_key] += 1
 else:
 pos30_offchain[pos30_char] += 1
 pos4_offchain[pos4_char] += 1
 combo_offchain[combo_key] += 1
 
 results.append({
 "layer1_identity": layer1_id,
 "layer2_identity": layer2_id,
 "layer3_identity": layer3_id,
 "position30_char": pos30_char,
 "position4_char": pos4_char,
 "combination": combo_key,
 "is_onchain": is_onchain
 })
 
 # Progress - Update file and print
 if i % 10 == 0 or i == 1:
 elapsed = time.time() - start_time
 rate = i / elapsed if elapsed > 0 else 0
 remaining = (count - i) / rate if rate > 0 else 0
 onchain_count = sum(1 for r in results if r["is_onchain"])
 progress_data = {
 "processed": i,
 "total": count,
 "onchain": onchain_count,
 "offchain": len(results) - onchain_count,
 "onchain_rate": (onchain_count / len(results) * 100) if results else 0,
 "elapsed_seconds": elapsed,
 "elapsed_minutes": elapsed / 60,
 "rate_per_second": rate,
 "eta_minutes": remaining / 60,
 "eta_seconds": remaining,
 "percent_complete": (i / count * 100) if count > 0 else 0,
 "status": "running"
 }
 
 # Write progress file
 try:
 with progress_file.open("w") as f:
 json.dump(progress_data, f, indent=2)
 except Exception:
 pass
 
 print(f" Processed: {i}/{count} ({i/count*100:.1f}%), On-chain: {onchain_count}/{len(results)} ({onchain_count/len(results)*100:.1f}%), "
 f"ETA: {remaining/60:.1f} min")
 
 elapsed = time.time() - start_time
 onchain_count = sum(1 for r in results if r['is_onchain'])
 
 # Final progress update
 progress_data = {
 "processed": len(results),
 "total": count,
 "onchain": onchain_count,
 "offchain": len(results) - onchain_count,
 "onchain_rate": (onchain_count / len(results) * 100) if results else 0,
 "elapsed_seconds": elapsed,
 "elapsed_minutes": elapsed / 60,
 "percent_complete": 100.0,
 "status": "completed"
 }
 
 try:
 with progress_file.open("w") as f:
 json.dump(progress_data, f, indent=2)
 except Exception:
 pass
 
 print()
 print(f"✅ Processed {len(results)} identities in {elapsed/60:.1f} minutes")
 print(f"✅ On-chain: {onchain_count}/{len(results)} ({onchain_count/len(results)*100:.1f}%)")
 print()
 
 # Train/Test Split (80/20)
 train_size = int(len(results) * 0.8)
 train_results = results[:train_size]
 test_results = results[train_size:]
 
 # Train: Baue Model
 train_pos30_on = Counter()
 train_pos30_off = Counter()
 train_pos4_on = Counter()
 train_pos4_off = Counter()
 train_combo_on = defaultdict(int)
 train_combo_off = defaultdict(int)
 
 for result in train_results:
 pos30_char = result["position30_char"]
 pos4_char = result["position4_char"]
 combo_key = result["combination"]
 is_onchain = result["is_onchain"]
 
 if is_onchain:
 train_pos30_on[pos30_char] += 1
 train_pos4_on[pos4_char] += 1
 train_combo_on[combo_key] += 1
 else:
 train_pos30_off[pos30_char] += 1
 train_pos4_off[pos4_char] += 1
 train_combo_off[combo_key] += 1
 
 # Test: Berechne Accuracy
 rules = {
 "position30_only": {"correct": 0, "total": 0},
 "position4_only": {"correct": 0, "total": 0},
 "both_agree": {"correct": 0, "total": 0},
 "position30_primary": {"correct": 0, "total": 0},
 "position4_primary": {"correct": 0, "total": 0},
 "combination": {"correct": 0, "total": 0}
 }
 
 for result in test_results:
 pos30_char = result["position30_char"]
 pos4_char = result["position4_char"]
 combo_key = result["combination"]
 is_onchain = result["is_onchain"]
 
 # Position 30 only
 pos30_on = train_pos30_on.get(pos30_char, 0)
 pos30_off = train_pos30_off.get(pos30_char, 0)
 pos30_total = pos30_on + pos30_off
 if pos30_total > 0:
 pred30 = (pos30_on / pos30_total) > 0.5
 rules["position30_only"]["total"] += 1
 if pred30 == is_onchain:
 rules["position30_only"]["correct"] += 1
 
 # Position 4 only
 pos4_on = train_pos4_on.get(pos4_char, 0)
 pos4_off = train_pos4_off.get(pos4_char, 0)
 pos4_total = pos4_on + pos4_off
 if pos4_total > 0:
 pred4 = (pos4_on / pos4_total) > 0.5
 rules["position4_only"]["total"] += 1
 if pred4 == is_onchain:
 rules["position4_only"]["correct"] += 1
 
 # Both agree
 if pos30_total > 0 and pos4_total > 0:
 pred30 = (pos30_on / pos30_total) > 0.5
 pred4 = (pos4_on / pos4_total) > 0.5
 if pred30 == pred4:
 rules["both_agree"]["total"] += 1
 if pred30 == is_onchain:
 rules["both_agree"]["correct"] += 1
 
 # Position 30 primary
 if pos30_total > 0:
 pred = (pos30_on / pos30_total) > 0.5
 elif pos4_total > 0:
 pred = (pos4_on / pos4_total) > 0.5
 else:
 continue
 rules["position30_primary"]["total"] += 1
 if pred == is_onchain:
 rules["position30_primary"]["correct"] += 1
 
 # Position 4 primary
 if pos4_total > 0:
 pred = (pos4_on / pos4_total) > 0.5
 elif pos30_total > 0:
 pred = (pos30_on / pos30_total) > 0.5
 else:
 continue
 rules["position4_primary"]["total"] += 1
 if pred == is_onchain:
 rules["position4_primary"]["correct"] += 1
 
 # Combination
 combo_on = train_combo_on.get(combo_key, 0)
 combo_off = train_combo_off.get(combo_key, 0)
 combo_total = combo_on + combo_off
 if combo_total > 0:
 pred_combo = (combo_on / combo_total) > 0.5
 rules["combination"]["total"] += 1
 if pred_combo == is_onchain:
 rules["combination"]["correct"] += 1
 
 # Berechne Accuracies
 for rule_name, rule_data in rules.items():
 if rule_data["total"] > 0:
 rule_data["accuracy"] = (rule_data["correct"] / rule_data["total"]) * 100
 else:
 rule_data["accuracy"] = 0
 
 return {
 "total_processed": len(results),
 "train_size": train_size,
 "test_size": len(test_results),
 "onchain_count": sum(1 for r in results if r["is_onchain"]),
 "offchain_count": sum(1 for r in results if not r["is_onchain"]),
 "onchain_rate": sum(1 for r in results if r["is_onchain"]) / len(results) * 100 if results else 0,
 "position30_onchain": dict(pos30_onchain),
 "position30_offchain": dict(pos30_offchain),
 "position4_onchain": dict(pos4_onchain),
 "position4_offchain": dict(pos4_offchain),
 "rules": rules,
 "elapsed_minutes": elapsed / 60,
 "results_sample": results[:20]
 }

def main():
 """Hauptfunktion."""
 import argparse
 parser = argparse.ArgumentParser()
 parser.add_argument("--count", type=int, default=500, help="Number of identities to test")
 args = parser.parse_args()
 
 print()
 print("⚠️ WARNING: This will make REAL RPC calls to the Qubic blockchain!")
 print(f" Testing {args.count} identities with live on-chain validation")
 print(" Starting in 3 seconds...")
 print()
 time.sleep(3)
 
 # Teste Kombination
 result = test_combination_live(args.count)
 
 if "error" in result:
 print(f"❌ Error: {result['error']}")
 return
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("RESULTS - LIVE RPC VALIDATION")
 print("=" * 80)
 print()
 
 print(f"Total Processed: {result['total_processed']}")
 print(f"Train Size: {result['train_size']}")
 print(f"Test Size: {result['test_size']}")
 print(f"On-chain: {result['onchain_count']}/{result['total_processed']} ({result['onchain_rate']:.1f}%)")
 print(f"Elapsed Time: {result['elapsed_minutes']:.1f} minutes")
 print()
 
 print("Rule Accuracies:")
 print()
 for rule_name, rule_data in sorted(result['rules'].items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
 acc = rule_data.get('accuracy', 0)
 correct = rule_data.get('correct', 0)
 total = rule_data.get('total', 0)
 print(f" {rule_name:25s}: {acc:5.1f}% ({correct}/{total})")
 
 print()
 
 # Beste Regel
 best_rule = max(result['rules'].items(), key=lambda x: x[1].get('accuracy', 0))
 print(f"✅ Best Rule: {best_rule[0]} ({best_rule[1].get('accuracy', 0):.1f}%)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_json = OUTPUT_DIR / "position30_position4_combination_live_rpc.json"
 with output_json.open("w") as f:
 json.dump(result, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position30_position4_combination_live_rpc_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 30 + Position 4 Combination - Live RPC Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Live RPC validation of Position 30 + Position 4 combination on {result['total_processed']} identities.\n\n")
 f.write(f"- **Total Processed**: {result['total_processed']}\n")
 f.write(f"- **Train Size**: {result['train_size']}\n")
 f.write(f"- **Test Size**: {result['test_size']}\n")
 f.write(f"- **On-chain Rate**: {result['onchain_rate']:.1f}%\n")
 f.write(f"- **Elapsed Time**: {result['elapsed_minutes']:.1f} minutes\n\n")
 
 f.write("## Results\n\n")
 f.write("| Rule | Accuracy | Correct/Total |\n")
 f.write("|------|----------|---------------|\n")
 
 for rule_name, rule_data in sorted(result['rules'].items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
 acc = rule_data.get('accuracy', 0)
 correct = rule_data.get('correct', 0)
 total = rule_data.get('total', 0)
 f.write(f"| {rule_name} | {acc:.1f}% | {correct}/{total} |\n")
 
 f.write("\n")
 f.write(f"## Best Rule\n\n")
 f.write(f"**{best_rule[0]}**: {best_rule[1].get('accuracy', 0):.1f}% accuracy\n\n")
 
 f.write("## Conclusion\n\n")
 if best_rule[1].get('accuracy', 0) >= 90:
 f.write("✅ **Combination validated with live RPC calls!**\n\n")
 f.write(f"Best combination achieves {best_rule[1].get('accuracy', 0):.1f}% accuracy ")
 f.write(f"on {result['test_size']} identities with real on-chain validation.\n\n")
 else:
 f.write("⚠️ **Combination accuracy lower than expected.**\n\n")
 f.write(f"Best combination achieves {best_rule[1].get('accuracy', 0):.1f}% accuracy.\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()

if __name__ == "__main__":
 main()

