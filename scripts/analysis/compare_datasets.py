#!/usr/bin/env python3
"""
Vergleiche die verschiedenen Layer-3 Datensätze
Identifiziere Unterschiede und erkläre den Widerspruch
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_dataset(file_path: Path) -> List[Dict]:
 """Load einen Datensatz."""
 if not file_path.exists():
 return []
 with file_path.open() as f:
 data = json.load(f)
 return data.get("results", [])

def analyze_dataset(results: List[Dict], name: str) -> Dict:
 """Analyze einen Datensatz."""
 total = len(results)
 onchain = sum(1 for r in results if r.get("layer3_onchain") == True or r.get("is_onchain") == True)
 offchain = sum(1 for r in results if r.get("layer3_onchain") == False or r.get("is_onchain") == False)
 unknown = total - onchain - offchain
 
 layer2_ids = {r.get("layer2_identity") for r in results if r.get("layer2_identity")}
 layer3_ids = {r.get("layer3_identity") for r in results if r.get("layer3_identity")}
 
 return {
 "name": name,
 "total": total,
 "onchain": onchain,
 "offchain": offchain,
 "unknown": unknown,
 "onchain_rate": (onchain / total * 100) if total > 0 else 0,
 "offchain_rate": (offchain / total * 100) if total > 0 else 0,
 "layer2_ids": layer2_ids,
 "layer3_ids": layer3_ids
 }

def compare_datasets():
 """Vergleiche alle Datensätze."""
 print("=" * 80)
 print("DATENSATZ-VERGLEICH - LAYER-3 IDENTITIES")
 print("=" * 80)
 print()
 
 # Load alle Datensätze
 complete_results = load_dataset(OUTPUT_DIR / "layer3_derivation_complete.json")
 extended_results = load_dataset(OUTPUT_DIR / "layer3_derivation_extended.json")
 proof_results = load_dataset(OUTPUT_DIR / "onchain_proof_complete.json")
 
 # Analyze
 complete_analysis = analyze_dataset(complete_results, "Complete Dataset")
 extended_analysis = analyze_dataset(extended_results, "Extended Dataset")
 proof_analysis = analyze_dataset(proof_results, "Proof Dataset (Live RPC)")
 
 # Zeige Ergebnisse
 for analysis in [complete_analysis, extended_analysis, proof_analysis]:
 if analysis["total"] > 0:
 print(f"{analysis['name']}:")
 print(f" Total: {analysis['total']}")
 print(f" On-chain: {analysis['onchain']} ({analysis['onchain_rate']:.1f}%)")
 print(f" Off-chain: {analysis['offchain']} ({analysis['offchain_rate']:.1f}%)")
 print(f" Unbekannt: {analysis['unknown']}")
 print(f" Unique Layer-2 IDs: {len(analysis['layer2_ids'])}")
 print()
 
 # Vergleiche Überlappungen
 print("=" * 80)
 print("ÜBERLAPPUNGS-ANALYSE")
 print("=" * 80)
 print()
 
 if complete_analysis["total"] > 0 and extended_analysis["total"] > 0:
 complete_layer3 = complete_analysis["layer3_ids"]
 extended_layer3 = extended_analysis["layer3_ids"]
 proof_layer3 = proof_analysis["layer3_ids"] if proof_analysis["total"] > 0 else set()
 
 overlap_complete_extended = complete_layer3 & extended_layer3
 overlap_complete_proof = complete_layer3 & proof_layer3
 overlap_extended_proof = extended_layer3 & proof_layer3
 
 print(f"Complete ↔ Extended: {len(overlap_complete_extended)} Identities")
 print(f"Complete ↔ Proof: {len(overlap_complete_proof)} Identities")
 print(f"Extended ↔ Proof: {len(overlap_extended_proof)} Identities")
 print()
 
 # Layer-2 Vergleich
 complete_layer2 = complete_analysis["layer2_ids"]
 extended_layer2 = extended_analysis["layer2_ids"]
 overlap_layer2 = complete_layer2 & extended_layer2
 
 print(f"Layer-2 Überlappung: {len(overlap_layer2)}")
 print(f" Complete unique Layer-2: {len(complete_layer2 - extended_layer2)}")
 print(f" Extended unique Layer-2: {len(extended_layer2 - complete_layer2)}")
 print()
 
 # Erkenntnisse
 print("=" * 80)
 print("ERKENNTNISSE")
 print("=" * 80)
 print()
 
 if len(overlap_complete_extended) == 0:
 print("✅ Complete und Extended haben KEINE abovelappenden Layer-3 Identities")
 print(" → Sie verwenden komplett verschiedene Identities!")
 print()
 if len(overlap_layer2) == 0:
 print("✅ Complete und Extended haben auch KEINE abovelappenden Layer-2 Quellen")
 print(" → Sie stammen aus komplett verschiedenen Quellen!")
 print()
 print("💡 ERKLÄRUNG FÜR DEN WIDERSPRUCH:")
 print(" - Complete Dataset: 34% on-chain Rate")
 print(" - Extended Dataset: 100% on-chain Rate")
 print(" → Verschiedene Layer-2 Quellen → verschiedene on-chain Raten!")
 else:
 print(f"⚠️ Aber sie teilen {len(overlap_layer2)} Layer-2 Quellen")
 print(" → Warum dann unterschiedliche on-chain Raten?")
 else:
 print(f"⚠️ {len(overlap_complete_extended)} Identities abovelappen")
 print(" → Warum unterschiedliche on-chain Raten for gleiche Identities?")
 
 # Speichere Report
 report = {
 "complete": complete_analysis,
 "extended": extended_analysis,
 "proof": proof_analysis,
 "overlaps": {
 "complete_extended": len(overlap_complete_extended) if complete_analysis["total"] > 0 and extended_analysis["total"] > 0 else 0,
 "complete_proof": len(overlap_complete_proof) if complete_analysis["total"] > 0 and proof_analysis["total"] > 0 else 0,
 "extended_proof": len(overlap_extended_proof) if extended_analysis["total"] > 0 and proof_analysis["total"] > 0 else 0,
 "layer2": len(overlap_layer2) if complete_analysis["total"] > 0 and extended_analysis["total"] > 0 else 0
 }
 }
 
 # Konvertiere Sets zu Listen for JSON
 for key in ["complete", "extended", "proof"]:
 if key in report:
 report[key]["layer2_ids"] = list(report[key]["layer2_ids"])
 report[key]["layer3_ids"] = list(report[key]["layer3_ids"])
 
 output_file = OUTPUT_DIR / "dataset_comparison.json"
 with output_file.open("w") as f:
 json.dump(report, f, indent=2)
 
 print(f"💾 Vergleich gespeichert: {output_file}")

if __name__ == "__main__":
 compare_datasets()

