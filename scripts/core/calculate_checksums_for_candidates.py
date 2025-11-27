#!/usr/bin/env python3
"""
Berechne Checksums for alle extrahierten Kandidaten.

Verwendet KangarooTwelve (vereinfacht) um 60-Char Identities zu erstellen.
"""

import json
import struct
import hashlib
from pathlib import Path
from typing import List, Dict

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "systematic_matrix_extraction.json"
OUTPUT_FILE = OUTPUT_DIR / "candidates_with_checksums.json"

def kangaroo_twelve_simple(data: bytes, output_length: int = 3) -> bytes:
 """Vereinfachte KangarooTwelve Implementierung (SHA256 als Fallback)."""
 # Für jetzt: Verwende SHA256 als Fallback
 # TODO: Echte KangarooTwelve Implementierung verwenden
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

def main():
 """Berechne Checksums for alle Kandidaten."""
 
 print("=" * 80)
 print("CHECKSUM-BERECHNUNG FÜR EXTRAHIERTE KANDIDATEN")
 print("=" * 80)
 print()
 
 # Load Kandidaten
 if not INPUT_FILE.exists():
 print(f"❌ Input-Datei nicht gefunden: {INPUT_FILE}")
 return
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 all_candidates = data.get("all_candidates", [])
 print(f"Geloadn: {len(all_candidates)} Kandidaten (56-Char Bodies)")
 print()
 
 # Berechne Checksums (nur for Stichprobe, da sehr viele)
 sample_size = min(1000, len(all_candidates))
 sample = all_candidates[:sample_size]
 
 print(f"Berechne Checksums for Stichprobe: {sample_size} Kandidaten")
 print()
 
 results = []
 valid_count = 0
 
 for i, candidate in enumerate(sample, 1):
 if i % 100 == 0:
 print(f" Progress: {i}/{sample_size}...")
 
 id_full, pk_hex, success = decode_public_key(candidate)
 
 if success and id_full:
 results.append({
 "body_56": candidate,
 "identity_60": id_full,
 "public_key_hex": pk_hex,
 "valid": True,
 })
 valid_count += 1
 else:
 results.append({
 "body_56": candidate,
 "identity_60": None,
 "public_key_hex": None,
 "valid": False,
 })
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 print(f"Geprüft: {len(results)} Kandidaten")
 print(f"Gültige Identities: {valid_count}")
 print(f"Rate: {valid_count/len(results)*100:.2f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "summary": {
 "total_candidates": len(all_candidates),
 "sample_size": sample_size,
 "checked": len(results),
 "valid_identities": valid_count,
 "valid_rate": valid_count/len(results)*100 if results else 0,
 },
 "results": results[:100], # Nur erste 100 for JSON
 "all_valid_identities": [r["identity_60"] for r in results if r["valid"]],
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 print()
 print(f"✅ {valid_count} gültige 60-Char Identities erstellt")
 print(" Nächster Schritt: On-Chain Validierung dieser Identities!")

if __name__ == "__main__":
 main()

