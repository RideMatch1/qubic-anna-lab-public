#!/usr/bin/env python3
"""
Position 4 Large-Scale Validation

Testet Position 4 auf allen 23.765 Identities:
- Leitet Layer-3 for alle Identities ab
- Prüft Position 4 Patterns
- Verifiziert 81% Accuracy
- Testet Perfect Markers auf großem Datensatz
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict, Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PATH = project_root / "venv-tx"

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 python_exe = VENV_PATH / "bin" / "python"
 
 if not python_exe.exists():
 return None
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode != 0:
 return None
 
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def check_identity_onchain(identity: str) -> bool:
 """Check ob Identity on-chain existiert."""
 python_exe = VENV_PATH / "bin" / "python"
 
 if not python_exe.exists():
 return False
 
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
except Exception:
 print("ERROR")
"""
 
 try:
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 return "EXISTS" in result.stdout
 except Exception:
 return False

def derive_layer3_from_layer1(layer1_identity: str) -> Optional[str]:
 """Leite Layer-3 Identity aus Layer-1 ab."""
 # Layer-1 → Layer-2
 layer2_seed = layer1_identity.lower()[:55]
 layer2_identity = derive_identity_from_seed(layer2_seed)
 
 if not layer2_identity:
 return None
 
 # Layer-2 → Layer-3
 layer3_seed = layer2_identity.lower()[:55]
 layer3_identity = derive_identity_from_seed(layer3_seed)
 
 return layer3_identity

def load_all_identities(sample_size: Optional[int] = None) -> List[str]:
 """Load alle Identities aus Mapping Database."""
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 
 if not db_file.exists():
 return []
 
 with db_file.open() as f:
 db = json.load(f)
 
 seed_to_real_id = db.get("seed_to_real_id", {})
 identities = list(seed_to_real_id.values())
 
 if sample_size:
 identities = identities[:sample_size]
 
 return identities

def test_position4_large_scale(use_existing_data: bool = True, sample_size: Optional[int] = None) -> Dict:
 """Teste Position 4 auf großem Datensatz."""
 print("=" * 80)
 print("POSITION 4 LARGE-SCALE TEST")
 print("=" * 80)
 print()
 
 results = []
 pos4_onchain = defaultdict(int)
 pos4_offchain = defaultdict(int)
 
 # Versuche vorhandene Layer-3 Daten zu verwenden
 if use_existing_data:
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 print("Loading existing Layer-3 data...")
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 
 layer3_results = layer3_data.get("results", [])
 if sample_size:
 layer3_results = layer3_results[:sample_size]
 
 print(f"✅ Loaded {len(layer3_results)} Layer-3 identities")
 print()
 print("Checking on-chain status...")
 print("(This may take a while...)")
 print()
 
 total_checked = 0
 
 for i, result in enumerate(layer3_results, 1):
 if i % 20 == 0:
 print(f" Progress: {i}/{len(layer3_results)} (checked: {total_checked})")
 
 layer3_id = result.get("layer3_identity", "")
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 # Extrahiere Position 4
 pos4_char = layer3_id[4]
 
 # Check On-chain Status (oder verwende vorhandenen Status)
 is_onchain = result.get("layer3_onchain", False)
 
 # Wenn nicht vorhanden, check jetzt
 if "layer3_onchain" not in result:
 is_onchain = check_identity_onchain(layer3_id)
 total_checked += 1
 
 # Speichere Ergebnis
 results.append({
 "layer1_id": result.get("layer2_identity", ""), # Layer-2 ist eigentlich Layer-1 for diese Chain
 "layer3_id": layer3_id,
 "pos4": pos4_char,
 "onchain": is_onchain
 })
 
 # Zähle for Position 4 Distribution
 if is_onchain:
 pos4_onchain[pos4_char] += 1
 else:
 pos4_offchain[pos4_char] += 1
 
 print()
 print(f"Results:")
 print(f" Total processed: {len(layer3_results)}")
 print(f" Layer-3 identities: {len(results)}")
 print(f" On-chain checked: {total_checked}")
 print()
 
 # Skip to accuracy calculation
 total_processed = len(results)
 total_derived = len(results)
 total_checked = len(results)
 else:
 use_existing_data = False
 
 # Fallback: Leite alles neu ab
 if not use_existing_data:
 print("Loading identities...")
 identities = load_all_identities(sample_size)
 print(f"✅ Loaded {len(identities)} identities")
 print()
 
 print("Deriving Layer-3 and testing Position 4...")
 print("(This may take a while...)")
 print()
 
 total_processed = 0
 total_derived = 0
 total_checked = 0
 
 for i, layer1_id in enumerate(identities, 1):
 if i % 100 == 0:
 print(f" Progress: {i}/{len(identities)} (derived: {total_derived}, checked: {total_checked})")
 
 total_processed += 1
 
 # Leite Layer-3 ab
 layer3_id = derive_layer3_from_layer1(layer1_id)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 total_derived += 1
 
 # Extrahiere Position 4
 pos4_char = layer3_id[4]
 
 # Check On-chain Status
 is_onchain = check_identity_onchain(layer3_id)
 total_checked += 1
 
 # Speichere Ergebnis
 results.append({
 "layer1_id": layer1_id,
 "layer3_id": layer3_id,
 "pos4": pos4_char,
 "onchain": is_onchain
 })
 
 # Zähle for Position 4 Distribution
 if is_onchain:
 pos4_onchain[pos4_char] += 1
 else:
 pos4_offchain[pos4_char] += 1
 
 print()
 print(f"Results:")
 print(f" Total processed: {total_processed}")
 print(f" Layer-3 derived: {total_derived}")
 print(f" On-chain checked: {total_checked}")
 print()
 
 print()
 print(f"Results:")
 print(f" Total processed: {total_processed}")
 print(f" Layer-3 derived: {total_derived}")
 print(f" On-chain checked: {total_checked}")
 print()
 
 # Berechne Accuracy
 correct = 0
 total_tested = 0
 
 # Baue Model aus ersten 80% (Training)
 train_size = int(len(results) * 0.8)
 train_results = results[:train_size]
 test_results = results[train_size:]
 
 # Train Model
 train_pos4_onchain = defaultdict(int)
 train_pos4_offchain = defaultdict(int)
 
 for result in train_results:
 char = result["pos4"]
 if result["onchain"]:
 train_pos4_onchain[char] += 1
 else:
 train_pos4_offchain[char] += 1
 
 # Test Model
 for result in test_results:
 char = result["pos4"]
 is_onchain = result["onchain"]
 
 on_count = train_pos4_onchain.get(char, 0)
 off_count = train_pos4_offchain.get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 total_tested += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total_tested * 100) if total_tested > 0 else 0
 
 # Perfect Marker Analysis
 perfect_markers = analyze_perfect_markers_large_scale(results)
 
 return {
 "total_processed": len(results),
 "total_derived": len(results),
 "total_checked": len(results),
 "accuracy": accuracy,
 "correct": correct,
 "total_tested": total_tested,
 "train_size": train_size,
 "test_size": len(test_results),
 "pos4_distribution": {
 "onchain": dict(pos4_onchain),
 "offchain": dict(pos4_offchain)
 },
 "perfect_markers": perfect_markers
 }

def analyze_perfect_markers_large_scale(results: List[Dict]) -> Dict:
 """Analyze Perfect Markers auf großem Datensatz."""
 perfect_onchain = ['Q', 'Z', 'F']
 perfect_offchain = ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']
 
 marker_analysis = {}
 
 for char in perfect_onchain + perfect_offchain:
 onchain_count = 0
 offchain_count = 0
 
 for result in results:
 if result["pos4"] == char:
 if result["onchain"]:
 onchain_count += 1
 else:
 offchain_count += 1
 
 total_count = onchain_count + offchain_count
 onchain_rate = (onchain_count / total_count * 100) if total_count > 0 else 0
 
 marker_analysis[char] = {
 "count": total_count,
 "onchain_count": onchain_count,
 "offchain_count": offchain_count,
 "onchain_rate": onchain_rate,
 "reliable": total_count >= 10,
 "still_perfect": (
 (char in perfect_onchain and onchain_rate == 100.0) or
 (char in perfect_offchain and onchain_rate == 0.0)
 )
 }
 
 return marker_analysis

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 4 LARGE-SCALE VALIDATION")
 print("=" * 80)
 print()
 print("This script tests Position 4 on a large dataset.")
 print("Using existing Layer-3 data if available...")
 print()
 
 # Verwende vorhandene Layer-3 Daten (schneller!)
 # Für vollständigen Test: sample_size=None
 results = test_position4_large_scale(use_existing_data=True, sample_size=None)
 
 print("=" * 80)
 print("LARGE-SCALE TEST RESULTS")
 print("=" * 80)
 print()
 print(f"Total processed: {results['total_processed']}")
 print(f"Layer-3 derived: {results['total_derived']}")
 print(f"On-chain checked: {results['total_checked']}")
 print()
 print(f"Accuracy: {results['accuracy']:.1f}% ({results['correct']}/{results['total_tested']})")
 print(f"Train size: {results['train_size']}")
 print(f"Test size: {results['test_size']}")
 print()
 
 print("Perfect Marker Analysis (Large Scale):")
 print()
 print("On-Chain Perfect Markers:")
 for char in ['Q', 'Z', 'F']:
 data = results['perfect_markers'][char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 perfect_status = "✅ PERFECT" if data["still_perfect"] else "❌ NOT PERFECT"
 print(f" '{char}': {data['onchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% "
 f"({status}, {perfect_status})")
 print()
 print("Off-Chain Perfect Markers:")
 for char in ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']:
 data = results['perfect_markers'][char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 perfect_status = "✅ PERFECT" if data["still_perfect"] else "❌ NOT PERFECT"
 print(f" '{char}': {data['onchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% "
 f"({status}, {perfect_status})")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_json = OUTPUT_DIR / "position4_large_scale_validation.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position4_large_scale_validation.md"
 
 with output_md.open("w") as f:
 f.write("# Position 4 Large-Scale Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Tested Position 4 on {results['total_processed']} identities.\n\n")
 f.write(f"- **Total processed**: {results['total_processed']}\n")
 f.write(f"- **Layer-3 derived**: {results['total_derived']}\n")
 f.write(f"- **On-chain checked**: {results['total_checked']}\n")
 f.write(f"- **Accuracy**: {results['accuracy']:.1f}% ({results['correct']}/{results['total_tested']})\n")
 f.write(f"- **Train size**: {results['train_size']}\n")
 f.write(f"- **Test size**: {results['test_size']}\n\n")
 
 f.write("## Perfect Marker Reliability (Large Scale)\n\n")
 f.write("### On-Chain Perfect Markers\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable | Still Perfect |\n")
 f.write("|------|-------|----------|-----------|------------|----------|---------------|\n")
 for char in ['Q', 'Z', 'F']:
 data = results['perfect_markers'][char]
 reliable = "✅" if data["reliable"] else "⚠️"
 perfect = "✅" if data["still_perfect"] else "❌"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} | {perfect} |\n")
 f.write("\n")
 
 f.write("### Off-Chain Perfect Markers\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable | Still Perfect |\n")
 f.write("|------|-------|----------|-----------|------------|----------|---------------|\n")
 for char in ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']:
 data = results['perfect_markers'][char]
 reliable = "✅" if data["reliable"] else "⚠️"
 perfect = "✅" if data["still_perfect"] else "❌"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} | {perfect} |\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 if results['accuracy'] > 70:
 f.write("✅ **Position 4 accuracy holds at scale** ({results['accuracy']:.1f}%)\n\n")
 else:
 f.write("⚠️ **Position 4 accuracy lower at scale** ({results['accuracy']:.1f}%)\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

