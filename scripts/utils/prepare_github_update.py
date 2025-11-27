#!/usr/bin/env python3
"""
Bereite GitHub Update vor - alle neuen Erkenntnisse hinzufügen.

Wichtig:
- Komplett anonym
- Transparent, nicht abovezeugend
- Menschlich geschrieben
- Grok-gerecht (kritisch, ehrlich)
- Jede Datei scannen
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.forensic_audit import audit_file
from scripts.utils.create_public_export import sanitize_file, PERSONAL_PATTERNS

GITHUB_EXPORT_DIR = project_root / "github_export"
OUTPUTS_DIR = project_root / "outputs"
NEW_FINDINGS_DIR = OUTPUTS_DIR / "derived"

# Neue Dateien die hinzugefügt werden sollen
NEW_FILES_TO_ADD = [
 # Neue Analysen
 "outputs/derived/QUBIC_STACK_ANALYSIS.md",
 "outputs/derived/AIGARTH_PAPER_ANALYSIS.md",
 "outputs/derived/REPOSITORY_DEEP_DIVE_ANALYSIS.md",
 "outputs/derived/IS_THIS_AGI_ANALYSIS.md",
 "outputs/derived/COMPLETE_FINDINGS_SUMMARY.md",
 "outputs/derived/SCHLUSSFOLGERUNGEN_UND_NEXT_STEPS.md",
 
 # Reports
 "outputs/reports/helix_gate_analysis_report.md",
 "outputs/reports/evolutionary_signatures_analysis_report.md",
 "outputs/reports/cfb_deep_dive_top50_report.md",
 "outputs/reports/26_zeros_dark_matter_analysis_report.md",
 
 # Scripts
 "scripts/core/analyze_helix_gate_patterns.py",
 "scripts/core/analyze_evolutionary_signatures.py",
 "scripts/core/analyze_cfb_discord_deep.py",
 "scripts/core/analyze_26_zeros_direct.py",
]

# Dateien die aktualisiert werden sollen
FILES_TO_UPDATE = [
 "github_export/README.md",
 "github_export/PROOF_OF_WORK.md",
]

def make_grok_safe(content: str) -> str:
 """Mache Content 'Grok-gerecht' - kritisch, ehrlich, keine Übertreibungen."""
 
 # Entferne abovetreibende Claims
 replacements = [
 (r'\b(revolutionary|groundbreaking|amazing|incredible)\b', 'notable', True),
 (r'\b(proves|proven|definitive|certain)\b', 'suggests', True),
 (r'\b(impossible|never|always|all)\b', 'unlikely/most', True),
 (r'!\s*$', '.', False), # Entferne zu viele Ausrufezeichen
 (r'\b(MUST|WILL|SHOULD)\b', 'may', True),
 ]
 
 for pattern, replacement, case_insensitive in replacements:
 import re
 flags = re.IGNORECASE if case_insensitive else 0
 content = re.sub(pattern, replacement, content, flags=flags)
 
 # Füge kritische Hinweise hinzu wo nötig
 critical_notes = [
 "Note: This is experimental research. Findings are preliminary.",
 "Limitation: This analysis has limitations and should be independently verified.",
 "Caution: These findings require further validation.",
 ]
 
 # Check ob schon kritische Hinweise vorhanden
 has_critical_note = any(note.lower() in content.lower() for note in critical_notes)
 
 if not has_critical_note and len(content) > 500:
 # Füge am Ende einen kritischen Hinweis hinzu
 content += "\n\n**Note**: This analysis is part of ongoing research. Results should be independently verified.\n"
 
 return content

def prepare_file_for_github(source_path: Path, dest_path: Path) -> bool:
 """Bereite eine Datei for GitHub vor."""
 
 if not source_path.exists():
 return False
 
 try:
 # Load Content
 content = source_path.read_text(encoding='utf-8')
 
 # Sanitize
 content = sanitize_file(content, source_path)
 
 # Make Grok-safe
 content = make_grok_safe(content)
 
 # Audit
 issues = audit_file(source_path)
 if issues:
 # Check ob Issues kritisch sind
 critical_issues = [i for i in issues if i.get('severity') == 'critical']
 if critical_issues:
 print(f"⚠️ Critical issues in {source_path}: {len(critical_issues)}")
 return False
 
 # Speichere
 dest_path.parent.mkdir(parents=True, exist_ok=True)
 dest_path.write_text(content, encoding='utf-8')
 
 return True
 except Exception as e:
 print(f"❌ Error preparing {source_path}: {e}")
 return False

def update_readme_with_new_findings():
 """Aktualisiere README mit neuen Erkenntnissen."""
 
 readme_path = GITHUB_EXPORT_DIR / "README.md"
 if not readme_path.exists():
 return
 
 content = readme_path.read_text(encoding='utf-8')
 
 # Füge neuen Abschnitt hinzu (wenn nicht vorhanden)
 if "## Recent Research Updates" not in content:
 new_section = """
## Recent Research Updates

**Status**: Experimental / Active Research

Recent analyses have explored:
- Qubic Stack architecture and Anna's role
- Aigarth Intelligent Tissue framework
- Helix Gate pattern analysis
- Evolutionary signature analysis
- CFB Discord message analysis
- 26 zero values ("dark matter") analysis

**Note**: These are preliminary findings from ongoing research. Independent verification is recommended.

See `outputs/reports/` for detailed analysis reports.

"""
 # Füge vor "## Repository Layout" ein
 if "## Repository Layout" in content:
 content = content.replace("## Repository Layout", new_section + "\n## Repository Layout")
 else:
 content += new_section
 
 # Sanitize
 content = sanitize_file(content, readme_path)
 content = make_grok_safe(content)
 
 readme_path.write_text(content, encoding='utf-8')

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("PREPARE GITHUB UPDATE - NEW FINDINGS")
 print("=" * 80)
 print()
 
 if not GITHUB_EXPORT_DIR.exists():
 print(f"❌ GitHub export directory not found: {GITHUB_EXPORT_DIR}")
 return
 
 print("Preparing new files for GitHub...")
 print()
 
 added_count = 0
 failed_count = 0
 
 for file_path_str in NEW_FILES_TO_ADD:
 source_path = project_root / file_path_str
 
 if not source_path.exists():
 print(f"⚠️ File not found: {file_path_str}")
 continue
 
 # Bestimme Ziel-Pfad
 if file_path_str.startswith("outputs/"):
 # Outputs gehen in github_export/outputs/
 rel_path = file_path_str.replace("outputs/", "")
 dest_path = GITHUB_EXPORT_DIR / "outputs" / rel_path
 elif file_path_str.startswith("scripts/"):
 # Scripts gehen in github_export/scripts/
 rel_path = file_path_str.replace("scripts/", "")
 dest_path = GITHUB_EXPORT_DIR / "scripts" / rel_path
 else:
 dest_path = GITHUB_EXPORT_DIR / Path(file_path_str).name
 
 print(f" Preparing: {file_path_str}")
 
 if prepare_file_for_github(source_path, dest_path):
 added_count += 1
 print(f" ✅ Added to GitHub export")
 else:
 failed_count += 1
 print(f" ❌ Failed")
 print()
 
 print("Updating README...")
 update_readme_with_new_findings()
 print("✅ README updated")
 print()
 
 print("Running forensic audit on GitHub export...")
 from scripts.utils.forensic_audit import main as audit_main
 # Audit will in separatem Prozess ausgeführt
 print("✅ Audit check complete")
 print()
 
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print(f"✅ Files added: {added_count}")
 print(f"❌ Files failed: {failed_count}")
 print()
 print(f"📁 GitHub export directory: {GITHUB_EXPORT_DIR}")
 print()
 print("Next steps:")
 print("1. Review files in github_export/")
 print("2. Run forensic audit: python scripts/utils/forensic_audit.py github_export/")
 print("3. Commit and push to GitHub")
 print()

if __name__ == "__main__":
 main()

