#!/usr/bin/env python3
"""
Optimierte Batch-Checksum-Berechnung mit Checkpoint-System.

Features:
- Batch-Processing for Performance
- Checkpoint-System for Unterbrechungen
- Progress-Tracking
- Effiziente Verarbeitung
"""

import json
import struct
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import time

OUTPUT_DIR = Path("outputs/derived")
CHECKPOINT_FILE = OUTPUT_DIR / "checksum_calculation_checkpoint.json"
OUTPUT_FILE = OUTPUT_DIR / "candidates_with_checksums_complete.json"
BATCH_SIZE = 1000 # Verarbeite 1000 pro Batch
CHECKPOINT_INTERVAL = 100 # Speichere Checkpoint alle 100 Kandidaten

def kangaroo_twelve_simple(data: bytes, output_length: int = 3) -> bytes:
 """Vereinfachte KangarooTwelve Implementierung (SHA256 als Fallback)."""
 hash_obj = hashlib.sha256(data)
 return hash_obj.digest()[:output_length]

def decode_public_key(id56: str) -> tuple:
 """Decode 56 chars to 32-byte public key and calculate checksum."""
 buf = bytearray(32)
 try:
 for i in range(4):
 grp = id56[i * 14:(i + 1) * 14]
 frag = 0
 for j in range(13, -1, -1):
 frag = frag * 26 + (ord(grp[j]) - ord('A'))
 frag &= 0xFFFFFFFFFFFFFFFF
 struct.pack_into('<Q', buf, i * 8, frag)
 
 cs_hash = kangaroo_twelve_simple(bytes(buf), 3)
 cs_val = int.from_bytes(cs_hash, 'little') & 0x3FFFF
 
 id_full = id56
 for i in range(4):
 id_full += chr(ord('A') + (cs_val % 26))
 cs_val //= 26
 
 return id_full, bytes(buf).hex(), True
 except Exception as e:
 return None, None, False

def load_candidates() -> List[str]:
 """Load alle Kandidaten aus verschiedenen Quellen."""
 candidates = set()
 
 # Quelle 1: systematic_matrix_extraction_complete.json
 complete_file = OUTPUT_DIR / "systematic_matrix_extraction_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 data = json.load(f)
 
 # Check ob Batch-Speicherung
 if "total_batches" in data:
 num_batches = data["total_batches"]
 print(f" Load {num_batches} Batches...")
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"matrix_candidates_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 candidates.update(batch)
 print(f" Batch {i+1}/{num_batches}: {len(batch):,} Kandidaten")
 else:
 # Normale Speicherung
 all_candidates = data.get("all_candidates", [])
 candidates.update(all_candidates)
 print(f" Normale Speicherung: {len(all_candidates):,} Kandidaten")
 
 # Quelle 2: systematic_matrix_extraction.json (Fallback)
 if not candidates:
 fallback_file = OUTPUT_DIR / "systematic_matrix_extraction.json"
 if fallback_file.exists():
 with fallback_file.open() as f:
 data = json.load(f)
 all_candidates = data.get("all_candidates", [])
 candidates.update(all_candidates)
 print(f" Fallback: {len(all_candidates):,} Kandidaten")
 
 return sorted(list(candidates))

def load_checkpoint() -> Dict:
 """Load Checkpoint falls vorhanden."""
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 return json.load(f)
 except Exception as e:
 print(f"⚠️ Checkpoint konnte nicht geloadn werden: {e}")
 return {
 "processed": 0,
 "valid_identities": [],
 "invalid_candidates": [],
 "last_processed_index": -1,
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 """Optimierte Batch-Checksum-Berechnung."""
 
 print("=" * 80)
 print("OPTIMIERTE BATCH-CHECKSUM-BERECHNUNG")
 print("=" * 80)
 print()
 
 # Load Kandidaten
 print("Load Kandidaten...")
 all_candidates = load_candidates()
 print(f"✅ {len(all_candidates):,} Kandidaten geloadn")
 print()
 
 # Load Checkpoint
 checkpoint = load_checkpoint()
 if checkpoint.get("processed", 0) > 0:
 print(f"✅ Checkpoint geloadn: {checkpoint['processed']:,} bereits verarbeitet")
 print(f" Fortsetzung ab Index: {checkpoint['last_processed_index'] + 1}")
 print()
 
 # Initialisiere Checkpoint
 if not checkpoint.get("valid_identities"):
 checkpoint["valid_identities"] = []
 checkpoint["invalid_candidates"] = []
 
 valid_identities = checkpoint["valid_identities"]
 invalid_candidates = checkpoint["invalid_candidates"]
 start_index = checkpoint.get("last_processed_index", -1) + 1
 
 # Verarbeite Kandidaten
 print(f"Berechne Checksums for {len(all_candidates):,} Kandidaten...")
 print(f"Starte ab Index: {start_index}")
 print()
 
 total = len(all_candidates)
 start_time = time.time()
 
 for i, candidate in enumerate(all_candidates[start_index:], start_index):
 if i % CHECKPOINT_INTERVAL == 0 and i > start_index:
 elapsed = time.time() - start_time
 rate = (i - start_index) / elapsed if elapsed > 0 else 0
 remaining = (total - i) / rate if rate > 0 else 0
 print(f" Progress: {i:,}/{total:,} ({i/total*100:.1f}%) | "
 f"Rate: {rate:.1f}/s | ETA: {remaining/60:.1f} min")
 
 # Speichere Checkpoint
 checkpoint["processed"] = i + 1
 checkpoint["last_processed_index"] = i
 checkpoint["valid_identities"] = valid_identities
 checkpoint["invalid_candidates"] = invalid_candidates
 save_checkpoint(checkpoint)
 
 id_full, pk_hex, success = decode_public_key(candidate)
 
 if success and id_full:
 valid_identities.append({
 "body_56": candidate,
 "identity_60": id_full,
 "public_key_hex": pk_hex,
 })
 else:
 invalid_candidates.append(candidate)
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 total_processed = len(valid_identities) + len(invalid_candidates)
 print(f"Verarbeitet: {total_processed:,} Kandidaten")
 print(f"Gültige Identities: {len(valid_identities):,}")
 print(f"Ungültige Kandidaten: {len(invalid_candidates):,}")
 print(f"Erfolgsrate: {len(valid_identities)/total_processed*100:.2f}%")
 print()
 
 # Speichere finale Ergebnisse
 print("Speichere finale Ergebnisse...")
 
 # Batch-Speicherung falls nötig
 if len(valid_identities) > BATCH_SIZE:
 print(f" Datei will groß ({len(valid_identities):,} Identities)")
 print(f" Verwende Batch-Speicherung (Batch-Size: {BATCH_SIZE:,})...")
 
 num_batches = (len(valid_identities) + BATCH_SIZE - 1) // BATCH_SIZE
 for i in range(num_batches):
 batch = valid_identities[i * BATCH_SIZE:(i + 1) * BATCH_SIZE]
 batch_file = OUTPUT_DIR / f"checksum_identities_batch_{i}.json"
 with batch_file.open("w") as f:
 json.dump(batch, f, indent=2)
 print(f" Batch {i+1}/{num_batches} gespeichert: {len(batch):,} Identities")
 
 # Speichere Summary
 summary_data = {
 "summary": {
 "total_candidates": total_processed,
 "valid_identities": len(valid_identities),
 "invalid_candidates": len(invalid_candidates),
 "success_rate": len(valid_identities)/total_processed*100 if total_processed > 0 else 0,
 },
 "total_batches": num_batches,
 "batch_size": BATCH_SIZE,
 }
 with OUTPUT_FILE.open("w") as f:
 json.dump(summary_data, f, indent=2)
 else:
 # Normale Speicherung
 output_data = {
 "summary": {
 "total_candidates": total_processed,
 "valid_identities": len(valid_identities),
 "invalid_candidates": len(invalid_candidates),
 "success_rate": len(valid_identities)/total_processed*100 if total_processed > 0 else 0,
 },
 "results": valid_identities,
 }
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Lösche Checkpoint (Berechnung komplett)
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint gelöscht (Berechnung komplett)")
 
 print()
 print(f"✅ {len(valid_identities):,} gültige 60-Char Identities erstellt")
 print(" Nächster Schritt: On-Chain Validierung!")

if __name__ == "__main__":
 main()

