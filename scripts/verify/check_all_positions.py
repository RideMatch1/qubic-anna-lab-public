#!/usr/bin/env python3
"""
Check alle Positionen in Schritten
Testet Position 201-300, 301-400, 401-500
"""

import subprocess
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

def check_position_range(start: int, end: int, limit: int = 100):
 """Check einen Positionen-Bereich."""
 print("=" * 80)
 print(f"PRÜFE POSITIONEN {start}-{end}")
 print("=" * 80)
 print()
 
 script_path = project_root / "scripts" / "verify" / "prove_all_onchain.py"
 
 cmd = [
 "python3",
 str(script_path),
 str(limit),
 str(start),
 str(end)
 ]
 
 print(f"Starte: {' '.join(cmd)}")
 print()
 
 result = subprocess.run(
 cmd,
 cwd=project_root,
 capture_output=True,
 text=True
 )
 
 if result.returncode == 0:
 print("✅ Erfolgreich abgeschlossen")
 print(result.stdout)
 else:
 print("❌ Fehler:")
 print(result.stderr)
 
 return result.returncode == 0

def main():
 """Check alle Positionen in Schritten."""
 print("=" * 80)
 print("VOLLSTÄNDIGE POSITIONEN-PRÜFUNG")
 print("=" * 80)
 print()
 print("Check Positionen in Schritten:")
 print(" - Position 201-300 (100 Identities)")
 print(" - Position 301-400 (100 Identities)")
 print(" - Position 401-500 (100 Identities)")
 print()
 print("Geschätzte Gesamtdauer: ~12 Minuten (3 × ~4 Minuten)")
 print()
 
 ranges = [
 (201, 300),
 (301, 400),
 (401, 500)
 ]
 
 results = []
 
 for start, end in ranges:
 success = check_position_range(start, end, limit=100)
 results.append({
 "range": f"{start}-{end}",
 "success": success
 })
 
 if not success:
 print(f"⚠️ Fehler bei Positionen {start}-{end}")
 break
 
 # Kurze Pause zwischen Bereichen
 if start != ranges[-1][0]:
 print()
 print("⏸️ Kurze Pause (5 Sekunden)...")
 time.sleep(5)
 print()
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 for result in results:
 status = "✅" if result["success"] else "❌"
 print(f"{status} Positionen {result['range']}: {'Erfolgreich' if result['success'] else 'Fehler'}")
 
 print()
 print("💾 Check Ergebnisse mit:")
 print(" python3 scripts/tools/check_proof_status.py")

if __name__ == "__main__":
 main()

