#!/usr/bin/env python3
"""
Kombiniert Basis-RPC-Daten (20k) mit der laufenden B/D-Validierung.
- Entfernt Duplikate pro Identity (Basisdaten haben Vorrang).
- Fügt Metadaten zu Quelle & validForTick hinzu.
- Liefert Überblick above Klassenverteilung (A/B/C/D) und On-Chain-Quote.

Ausgabe: outputs/derived/rpc_validation_pos27_extended_dataset.json
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent

BASE_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_20000_validated_data.json"
TARGETED_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_targeted_bd_results.json"
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_pos27_extended_dataset.json"

def load_base_entries() -> List[Dict]:
 if not BASE_FILE.exists():
 raise FileNotFoundError(f"Basisdatei fehlt: {BASE_FILE}")
 with BASE_FILE.open() as fh:
 return json.load(fh).get("data", [])

def load_targeted_entries() -> List[Dict]:
 if not TARGETED_FILE.exists():
 return []
 with TARGETED_FILE.open() as fh:
 data = json.load(fh)
 return data.get("data", [])

def normalize_entry(entry: Dict, source: str) -> Dict:
 identity = entry["identity"]
 seed = entry.get("seed", "")
 actual_char = identity[27].upper() if len(identity) > 27 else entry.get("actual", "?")
 normalized = {
 "identity": identity,
 "seed": seed,
 "actual": actual_char,
 "on_chain": entry.get("on_chain", False),
 "valid_for_tick": entry.get("valid_for_tick"),
 "has_activity": entry.get("has_activity", False),
 "source": source,
 }
 # Übernehme Zusatzinfos falls vorhanden
 if "predicted" in entry:
 normalized["predicted"] = entry["predicted"]
 if "is_correct" in entry:
 normalized["is_correct"] = entry["is_correct"]
 if "rpc" in entry and isinstance(entry["rpc"], dict):
 normalized["rpc_details"] = entry["rpc"]
 return normalized

def main() -> None:
 base_entries = load_base_entries()
 targeted_entries = load_targeted_entries()

 combined: Dict[str, Dict] = {}
 # Basis zuerst
 for entry in base_entries:
 combined[entry["identity"]] = normalize_entry(entry, "base_20k")

 # Dann B/D-Erweiterungen (nur neue Identities)
 for entry in targeted_entries:
 identity = entry["identity"]
 if identity in combined:
 continue
 normalized = normalize_entry(
 {
 "identity": identity,
 "seed": entry.get("seed", ""),
 "on_chain": entry.get("on_chain", False),
 "valid_for_tick": entry.get("rpc", {}).get("valid_for_tick"),
 "has_activity": entry.get("rpc", {}).get("has_activity", False),
 },
 "targeted_bd",
 )
 combined[identity] = normalized

 combined_list = list(combined.values())
 class_counts = Counter(entry["actual"] for entry in combined_list)
 on_chain_count = sum(1 for e in combined_list if e.get("on_chain"))

 output_payload = {
 "timestamp": datetime.now().isoformat(),
 "total_entries": len(combined_list),
 "class_distribution": dict(sorted(class_counts.items())),
 "on_chain_rate": {
 "count": on_chain_count,
 "percent": (on_chain_count / len(combined_list) * 100) if combined_list else 0.0,
 },
 "sources": {
 "base_20k": len(base_entries),
 "targeted_bd_total": len(targeted_entries),
 "combined_unique": len(combined_list),
 },
 "data": combined_list,
 }

 OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as fh:
 json.dump(output_payload, fh, indent=2)

 print(f"✅ Erweiterter Datensatz gespeichert: {OUTPUT_FILE}")
 print(f" Klassenverteilung: {dict(sorted(class_counts.items()))}")
 print(f" On-Chain: {on_chain_count}/{len(combined_list)} ({output_payload['on_chain_rate']['percent']:.2f}%)")

if __name__ == "__main__":
 main()

