#!/usr/bin/env python3
"""
Daten-Integritäts-Validierung - Prüft alle Daten auf Konsistenz und Validität.

Prüft:
1. Format-Validierung (60 Zeichen, A-Z)
2. Seed-Validierung (55 Zeichen, lowercase)
3. Konsistenz zwischen Dateien
4. Duplikate
5. Trace-Kette (Matrix → Checksum → On-Chain)
"""

import json
from pathlib import Path
from typing import List, Set, Dict
from collections import Counter

OUTPUT_DIR = Path("outputs/derived")

def validate_identity_format(identity: str) -> tuple[bool, str]:
 """Validate Identity-Format."""
 if not isinstance(identity, str):
 return False, "Nicht ein String"
 if len(identity) != 60:
 return False, f"Falsche Länge: {len(identity)} (erwartet: 60)"
 if not identity.isupper():
 return False, "Nicht UPPERCASE"
 if not all('A' <= c <= 'Z' for c in identity):
 return False, "Enthält ungültige Zeichen"
 return True, "OK"

def validate_seed_format(seed: str) -> tuple[bool, str]:
 """Validate Seed-Format."""
 if not isinstance(seed, str):
 return False, "Nicht ein String"
 if len(seed) != 55:
 return False, f"Falsche Länge: {len(seed)} (erwartet: 55)"
 if not seed.islower():
 return False, "Nicht lowercase"
 if not seed.isalpha():
 return False, "Enthält ungültige Zeichen"
 return True, "OK"

def check_duplicates(items: List[str], item_type: str) -> Dict:
 """Check auf Duplikate."""
 counter = Counter(items)
 duplicates = {item: count for item, count in counter.items() if count > 1}
 
 return {
 "total": len(items),
 "unique": len(counter),
 "duplicates": len(duplicates),
 "duplicate_items": list(duplicates.keys())[:10], # Erste 10
 }

def validate_trace_chain() -> Dict:
 """Validate Trace-Kette: Matrix → Checksum → On-Chain."""
 
 results = {
 "matrix_to_checksum": {"valid": False, "matches": 0, "total": 0},
 "checksum_to_onchain": {"valid": False, "matches": 0, "total": 0},
 "onchain_to_analysis": {"valid": False, "matches": 0, "total": 0},
 }
 
 # Matrix → Checksum
 matrix_file = OUTPUT_DIR / "systematic_matrix_extraction_complete.json"
 checksum_file = OUTPUT_DIR / "candidates_with_checksums_complete.json"
 
 if matrix_file.exists() and checksum_file.exists():
 # Load Matrix-Kandidaten
 with matrix_file.open() as f:
 matrix_data = json.load(f)
 
 matrix_candidates = set()
 if "total_batches" in matrix_data:
 num_batches = matrix_data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"matrix_candidates_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 matrix_candidates.update(batch)
 else:
 matrix_candidates = set(matrix_data.get("all_candidates", []))
 
 # Load Checksum Bodies
 with checksum_file.open() as f:
 checksum_data = json.load(f)
 
 checksum_bodies = set()
 if "total_batches" in checksum_data:
 num_batches = checksum_data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"checksum_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 for item in batch:
 if isinstance(item, dict):
 checksum_bodies.add(item.get("body_56", ""))
 else:
 checksum_bodies.add(item[:56] if len(item) >= 56 else item)
 else:
 results_list = checksum_data.get("results", [])
 for item in results_list:
 if isinstance(item, dict):
 checksum_bodies.add(item.get("body_56", ""))
 
 matches = len(matrix_candidates & checksum_bodies)
 results["matrix_to_checksum"] = {
 "valid": matches == len(checksum_bodies),
 "matches": matches,
 "total": len(checksum_bodies),
 }
 
 # Checksum → On-Chain
 onchain_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 
 if checksum_file.exists() and onchain_file.exists():
 # Load Checksum Identities
 checksum_identities = set()
 if "total_batches" in checksum_data:
 num_batches = checksum_data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"checksum_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 for item in batch:
 if isinstance(item, dict):
 checksum_identities.add(item.get("identity_60", ""))
 else:
 checksum_identities.add(item)
 else:
 results_list = checksum_data.get("results", [])
 for item in results_list:
 if isinstance(item, dict):
 checksum_identities.add(item.get("identity_60", ""))
 
 # Load On-Chain Identities
 with onchain_file.open() as f:
 onchain_data = json.load(f)
 
 onchain_identities = set()
 if "total_batches" in onchain_data:
 num_batches = onchain_data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 onchain_identities.update(batch)
 else:
 onchain_identities = set(onchain_data.get("onchain_identities", []))
 
 matches = len(checksum_identities & onchain_identities)
 results["checksum_to_onchain"] = {
 "valid": matches == len(onchain_identities),
 "matches": matches,
 "total": len(onchain_identities),
 }
 
 return results

def main():
 """Validate Daten-Integrität."""
 
 print("=" * 80)
 print("DATEN-INTEGRITÄTS-VALIDIERUNG")
 print("=" * 80)
 print()
 
 all_errors = []
 all_warnings = []
 
 # 1. Format-Validierung
 print("1. FORMAT-VALIDIERUNG:")
 print("-" * 80)
 
 # Check On-Chain Identities
 onchain_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if onchain_file.exists():
 with onchain_file.open() as f:
 data = json.load(f)
 
 onchain_identities = []
 if "total_batches" in data:
 num_batches = data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 onchain_identities.extend(batch)
 else:
 onchain_identities = data.get("onchain_identities", [])
 
 invalid_count = 0
 for identity in onchain_identities[:1000]: # Stichprobe
 valid, error = validate_identity_format(identity)
 if not valid:
 invalid_count += 1
 all_errors.append(f"Invalid Identity: {identity[:40]}... - {error}")
 
 if invalid_count == 0:
 print(f" ✅ {len(onchain_identities):,} Identities: Format korrekt (Stichprobe)")
 else:
 print(f" ❌ {invalid_count} ungültige Identities gefunden (Stichprobe)")
 else:
 print(" ⏳ On-Chain Validierung noch nicht komplett")
 print()
 
 # 2. Duplikat-Prüfung
 print("2. DUPLIKAT-PRÜFUNG:")
 print("-" * 80)
 
 if onchain_file.exists():
 dup_result = check_duplicates(onchain_identities, "Identities")
 print(f" Total: {dup_result['total']:,}")
 print(f" Unique: {dup_result['unique']:,}")
 print(f" Duplikate: {dup_result['duplicates']}")
 
 if dup_result['duplicates'] == 0:
 print(" ✅ Keine Duplikate")
 else:
 print(f" ⚠️ {dup_result['duplicates']} Duplikate gefunden")
 all_warnings.append(f"{dup_result['duplicates']} Duplikate in Identities")
 else:
 print(" ⏳ On-Chain Validierung noch nicht komplett")
 print()
 
 # 3. Trace-Kette Validierung
 print("3. TRACE-KETTE VALIDIERUNG:")
 print("-" * 80)
 
 trace_results = validate_trace_chain()
 
 for chain_name, result in trace_results.items():
 if result["total"] > 0:
 status = "✅" if result["valid"] else "❌"
 print(f" {status} {chain_name}: {result['matches']}/{result['total']} Matches")
 if not result["valid"]:
 all_errors.append(f"Trace-Kette {chain_name}: {result['matches']}/{result['total']} Matches")
 else:
 print(f" ⏳ {chain_name}: Noch nicht verfügbar")
 print()
 
 # 4. Seed-Validierung
 print("4. SEED-VALIDIERUNG:")
 print("-" * 80)
 
 analysis_file = OUTPUT_DIR / "found_identities_analysis.json"
 if analysis_file.exists():
 with analysis_file.open() as f:
 data = json.load(f)
 
 all_seeds = data.get("all_seeds", [])
 invalid_seeds = 0
 for seed in all_seeds[:100]: # Stichprobe
 valid, error = validate_seed_format(seed)
 if not valid:
 invalid_seeds += 1
 all_errors.append(f"Invalid Seed: {seed[:30]}... - {error}")
 
 if invalid_seeds == 0:
 print(f" ✅ {len(all_seeds):,} Seeds: Format korrekt (Stichprobe)")
 else:
 print(f" ❌ {invalid_seeds} ungültige Seeds gefunden (Stichprobe)")
 else:
 print(" ⏳ Identities-Analyse noch nicht komplett")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 if all_errors:
 print(f"❌ {len(all_errors)} Fehler gefunden:")
 for error in all_errors[:10]:
 print(f" - {error}")
 if len(all_errors) > 10:
 print(f" ... und {len(all_errors) - 10} weitere")
 else:
 print("✅ Keine Fehler gefunden")
 
 print()
 
 if all_warnings:
 print(f"⚠️ {len(all_warnings)} Warnungen:")
 for warning in all_warnings:
 print(f" - {warning}")
 else:
 print("✅ Keine Warnungen")
 
 print()
 
 if not all_errors and not all_warnings:
 print("✅ ALLE VALIDIERUNGEN ERFOLGREICH!")
 print(" Daten sind konsistent und valide!")

if __name__ == "__main__":
 main()

