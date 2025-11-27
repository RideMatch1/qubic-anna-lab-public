#!/usr/bin/env python3
"""
Komplette GitHub Update Vorbereitung - alle neuen Erkenntnisse.

Wichtig:
- Komplett anonym
- Transparent, nicht abovezeugend
- Menschlich geschrieben
- Grok-gerecht (kritisch, ehrlich, keine Übertreibungen)
- Jede Datei scannen und validaten
"""

import json
import re
import shutil
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.forensic_audit import audit_file, PATTERNS, SKIP_PATTERNS

GITHUB_EXPORT_DIR = project_root / "github_export"
OUTPUTS_DIR = project_root / "outputs"

# Neue Dateien die hinzugefügt werden sollen (nur öffentlich relevante)
NEW_PUBLIC_FILES = [
 # Neue Analysen (nur die, die öffentlich relevant sind)
 "outputs/derived/QUBIC_STACK_ANALYSIS.md",
 "outputs/derived/AIGARTH_PAPER_ANALYSIS.md",
 "outputs/derived/REPOSITORY_DEEP_DIVE_ANALYSIS.md",
 "outputs/derived/IS_THIS_AGI_ANALYSIS.md",
 "outputs/derived/COMPLETE_FINDINGS_SUMMARY.md",
 
 # Reports (nur die wichtigsten)
 "outputs/reports/helix_gate_analysis_report.md",
 "outputs/reports/evolutionary_signatures_analysis_report.md",
 "outputs/reports/26_zeros_dark_matter_analysis_report.md",
 
 # Scripts (nur die reproduzierbaren)
 "scripts/core/analyze_helix_gate_patterns.py",
 "scripts/core/analyze_evolutionary_signatures.py",
 "scripts/core/analyze_26_zeros_direct.py",
]

# Dateien die NICHT öffentlich sein sollen
EXCLUDE_FILES = [
 "outputs/derived/cfb_discord_messages/",
 "outputs/derived/*DISCORD*.md",
 "outputs/derived/*CFB*.md",
 "outputs/derived/*STRATEGY*.md",
 "outputs/derived/*CONTRACT*.md",
 "outputs/derived/*WALLET*.md",
 "outputs/derived/*TRANSACTION*.md",
 "outputs/derived/SCHLUSSFOLGERUNGEN_UND_NEXT_STEPS.md", # Zu intern
 "outputs/derived/DEEP_ANALYSIS_RESULTS.md", # Zu detailliert intern
 "scripts/core/analyze_cfb_discord_deep.py", # Discord-spezifisch
 "scripts/core/derive_layer3_identities.py", # Noch nicht fertig
 "scripts/core/analyze_identity_roles.py", # Noch nicht fertig
]

def make_grok_safe(content: str, file_path: Path) -> str:
 """Mache Content 'Grok-gerecht' - kritisch, ehrlich, keine Übertreibungen."""
 
 # Entferne abovetreibende Claims
 replacements = [
 # Übertreibungen → moderate Formulierungen
 (r'\b(revolutionary|groundbreaking|amazing|incredible|stunning)\b', 'notable', True),
 (r'\b(proves|proven|definitive|certain|guaranteed)\b', 'suggests', True),
 (r'\b(impossible|never|always|all|every)\b', 'unlikely/most/many', True),
 (r'!\s*$', '.', False), # Entferne zu viele Ausrufezeichen am Ende
 (r'\b(MUST|WILL|SHOULD)\b', 'may', True),
 (r'\b(perfect|perfectly)\b', 'high/strong', True),
 (r'\b(complete|completely)\b', 'extensive', True),
 
 # Entferne zu viele Emojis (falls welche drin sind)
 (r'[✅❌⚠️🎯📊💡🔬⭐]', '', False),
 
 # Entferne "This is interesting" etc.
 (r'\b(This is|It is) (interesting|important|notable)\b', 'Analysis shows', True),
 ]
 
 for pattern, replacement, case_insensitive in replacements:
 flags = re.IGNORECASE if case_insensitive else 0
 content = re.sub(pattern, replacement, content, flags=flags)
 
 # Füge kritische Hinweise hinzu wo nötig
 critical_notes = [
 "Note: This is experimental research. Findings are preliminary and require independent verification.",
 "Limitation: This analysis has limitations and should be independently verified.",
 "Caution: These findings require further validation.",
 "Important: This is ongoing research. Methods and interpretations may evolve.",
 ]
 
 # Check ob schon kritische Hinweise vorhanden
 has_critical_note = any(note.lower()[:20] in content.lower() for note in critical_notes)
 
 # Füge am Ende einen kritischen Hinweis hinzu wenn nötig
 if not has_critical_note and len(content) > 500 and file_path.suffix == '.md':
 # Check ob es ein Report ist
 if 'report' in file_path.name.lower() or 'analysis' in file_path.name.lower():
 content += "\n\n**Note**: This analysis is part of ongoing research. Results should be independently verified and may evolve as research continues.\n"
 
 return content

def remove_llm_phrases(content: str) -> str:
 """Entferne LLM-typische Phrasen."""
 
 llm_phrases = [
 r'\bAs you can see\b',
 r'\bTo summarize\b',
 r'\bIn conclusion\b',
 r'\bIt is important to note\b',
 r'\bIt should be noted\b',
 r'\bThis is interesting\b',
 r'\bThis is important\b',
 r'\bLet me explain\b',
 r'\bI should mention\b',
 ]
 
 for pattern in llm_phrases:
 content = re.sub(pattern, '', content, flags=re.IGNORECASE)
 
 # Entferne doppelte Leerzeilen
 content = re.sub(r'\n{3,}', '\n\n', content)
 
 return content

def sanitize_content(content: str, file_path: Path) -> str:
 """Sanitize Content for GitHub."""
 
 # Entferne persönliche Daten
 for pattern, replacement in [
 (r'/Users/[\w\-]+/', '/Users/user/'),
 (r'${USER}', 'user'),
 (r'Lukas\s+Hertle', 'Researcher'),
 ]:
 content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
 
 # Entferne absolute Paths (außer in Code-Blöcken)
 # Einfache Lösung: Ersetze in normalem Text
 lines = content.split('\n')
 in_code_block = False
 sanitized_lines = []
 
 for line in lines:
 if line.strip().startswith('```'):
 in_code_block = not in_code_block
 
 if not in_code_block:
 # Ersetze absolute Paths
 line = re.sub(r'/Users/[\w\-]+/', '${HOME}/', line)
 line = re.sub(r'/home/[\w\-]+/', '${HOME}/', line)
 
 sanitized_lines.append(line)
 
 content = '\n'.join(sanitized_lines)
 
 # Entferne LLM-Phrasen
 content = remove_llm_phrases(content)
 
 # Make Grok-safe
 content = make_grok_safe(content, file_path)
 
 return content

def prepare_file_for_github(source_path: Path, dest_path: Path) -> Dict:
 """Bereite eine Datei for GitHub vor."""
 
 result = {
 "success": False,
 "issues": [],
 "warnings": [],
 }
 
 if not source_path.exists():
 result["issues"].append("File not found")
 return result
 
 try:
 # Load Content
 content = source_path.read_text(encoding='utf-8')
 
 # Sanitize
 content = sanitize_content(content, source_path)
 
 # Audit
 audit_result = audit_file(source_path)
 if audit_result:
 # Filtere kritische Issues
 critical = [i for i in audit_result if i.get('severity') == 'critical']
 if critical:
 result["issues"].extend([f"Critical: {i.get('message', '')}" for i in critical])
 result["success"] = False
 return result
 
 # Warnungen sind OK, aber notieren
 warnings = [i for i in audit_result if i.get('severity') != 'critical']
 if warnings:
 result["warnings"].extend([f"Warning: {i.get('message', '')}" for i in warnings])
 
 # Speichere
 dest_path.parent.mkdir(parents=True, exist_ok=True)
 dest_path.write_text(content, encoding='utf-8')
 
 result["success"] = True
 return result
 
 except Exception as e:
 result["issues"].append(f"Error: {str(e)}")
 return result

def should_exclude_file(file_path: Path) -> bool:
 """Check ob Datei ausgeschlossen werden soll."""
 
 file_str = str(file_path)
 
 for exclude_pattern in EXCLUDE_FILES:
 if exclude_pattern in file_str:
 return True
 
 return False

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("PREPARE GITHUB UPDATE - ALL NEW FINDINGS")
 print("=" * 80)
 print()
 
 if not GITHUB_EXPORT_DIR.exists():
 print(f"❌ GitHub export directory not found: {GITHUB_EXPORT_DIR}")
 return
 
 print("Preparing new files for GitHub...")
 print()
 
 added_count = 0
 failed_count = 0
 skipped_count = 0
 
 for file_path_str in NEW_PUBLIC_FILES:
 source_path = project_root / file_path_str
 
 if not source_path.exists():
 print(f"⚠️ File not found: {file_path_str}")
 skipped_count += 1
 continue
 
 if should_exclude_file(source_path):
 print(f"⏭️ Excluded: {file_path_str}")
 skipped_count += 1
 continue
 
 # Bestimme Ziel-Pfad
 if file_path_str.startswith("outputs/"):
 rel_path = file_path_str.replace("outputs/", "")
 dest_path = GITHUB_EXPORT_DIR / "outputs" / rel_path
 elif file_path_str.startswith("scripts/"):
 rel_path = file_path_str.replace("scripts/", "")
 dest_path = GITHUB_EXPORT_DIR / "scripts" / rel_path
 else:
 dest_path = GITHUB_EXPORT_DIR / Path(file_path_str).name
 
 print(f" Preparing: {file_path_str}")
 
 result = prepare_file_for_github(source_path, dest_path)
 
 if result["success"]:
 added_count += 1
 if result["warnings"]:
 print(f" ✅ Added (with {len(result['warnings'])} warnings)")
 else:
 print(f" ✅ Added")
 else:
 failed_count += 1
 print(f" ❌ Failed: {', '.join(result['issues'])}")
 print()
 
 print("Updating README with new findings...")
 update_readme()
 print("✅ README updated")
 print()
 
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print(f"✅ Files added: {added_count}")
 print(f"❌ Files failed: {failed_count}")
 print(f"⏭️ Files skipped: {skipped_count}")
 print()
 print(f"📁 GitHub export directory: {GITHUB_EXPORT_DIR}")
 print()
 print("Next steps:")
 print("1. Review files in github_export/")
 print("2. Run forensic audit: python scripts/utils/forensic_audit.py github_export/")
 print("3. Test reproducibility")
 print("4. Commit and push to GitHub")
 print()

def update_readme():
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

Recent analyses have explored additional aspects of the matrix structure:

- **Qubic Stack Architecture**: Analysis of Anna's role in the 5-layer Qubic stack
- **Aigarth Framework**: Investigation of Aigarth Intelligent Tissue connection
- **Helix Gate Patterns**: 26,562 patterns found in matrix structure
- **Evolutionary Signatures**: Analysis of identity patterns suggesting evolutionary selection
- **26 Zero Values**: Analysis of "dark matter" control neurons

**Note**: These are preliminary findings from ongoing research. Independent verification is recommended. See `outputs/reports/` for detailed analysis reports.

**Important**: The matrix appears to be Aigarth Intelligent Tissue (ternary neural network weights), not encrypted data. This is based on repository analysis and statistical properties. However, this interpretation is still under investigation.

"""
 # Füge vor "## Repository Layout" ein
 if "## Repository Layout" in content:
 content = content.replace("## Repository Layout", new_section + "\n## Repository Layout")
 else:
 content += new_section
 
 # Sanitize
 content = sanitize_content(content, readme_path)
 
 readme_path.write_text(content, encoding='utf-8')

if __name__ == "__main__":
 main()

