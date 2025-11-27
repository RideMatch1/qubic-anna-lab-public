#!/usr/bin/env python3
"""
Final GitHub Preparation - alle neuen Erkenntnisse, Grok-safe, anonym.

Nutzt alle vorhandenen Scanner und macht alles Grok-gerecht.
"""

import re
import json
from pathlib import Path
from typing import List, Dict

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.create_public_export import humanize_content, sanitize_file, PERSONAL_PATTERNS
from scripts.utils.forensic_audit import audit_file

GITHUB_EXPORT = project_root / "github_export"

# Dateien die hinzugefügt werden sollen
FILES_TO_ADD = {
 "outputs/derived/QUBIC_STACK_ANALYSIS.md": "outputs/derived/QUBIC_STACK_ANALYSIS.md",
 "outputs/derived/AIGARTH_PAPER_ANALYSIS.md": "outputs/derived/AIGARTH_PAPER_ANALYSIS.md",
 "outputs/derived/REPOSITORY_DEEP_DIVE_ANALYSIS.md": "outputs/derived/REPOSITORY_DEEP_DIVE_ANALYSIS.md",
 "outputs/derived/IS_THIS_AGI_ANALYSIS.md": "outputs/derived/IS_THIS_AGI_ANALYSIS.md",
 "outputs/reports/helix_gate_analysis_report.md": "outputs/reports/helix_gate_analysis_report.md",
 "outputs/reports/evolutionary_signatures_analysis_report.md": "outputs/reports/evolutionary_signatures_analysis_report.md",
 "outputs/reports/26_zeros_dark_matter_analysis_report.md": "outputs/reports/26_zeros_dark_matter_analysis_report.md",
}

def make_grok_safe(text: str) -> str:
 """Mache Text Grok-safe - kritisch, ehrlich."""
 
 # Entferne Übertreibungen
 replacements = [
 (r'\b(revolutionary|groundbreaking|amazing|incredible)\b', 'notable', True),
 (r'\b(proves|proven|definitive|certain)\b', 'suggests', True),
 (r'\b(impossible|never|always|all)\b', 'unlikely/most/many', True),
 (r'!\s*$', '.', False),
 (r'\b(MUST|WILL|SHOULD)\b', 'may', True),
 ]
 
 for pattern, replacement, case_insensitive in replacements:
 flags = re.IGNORECASE if case_insensitive else 0
 text = re.sub(pattern, replacement, text, flags=flags)
 
 return text

def prepare_file(src: Path, dst: Path) -> bool:
 """Bereite Datei for GitHub vor."""
 
 if not src.exists():
 return False
 
 try:
 content = src.read_text(encoding='utf-8')
 
 # Sanitize
 content = humanize_content(content)
 
 # Grok-safe
 content = make_grok_safe(content)
 
 # Personal data entfernen
 for pattern, replacement in PERSONAL_PATTERNS:
 content = re.sub(pattern, replacement, content)
 
 # Speichere
 dst.parent.mkdir(parents=True, exist_ok=True)
 dst.write_text(content, encoding='utf-8')
 
 # Audit
 issues = audit_file(dst)
 critical = [i for i in issues if i.get('severity') == 'critical']
 if critical:
 print(f" ❌ Critical issues: {len(critical)}")
 return False
 
 return True
 except Exception as e:
 print(f" ❌ Error: {e}")
 return False

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("FINAL GITHUB PREPARATION")
 print("=" * 80)
 print()
 
 added = 0
 failed = 0
 
 for src_str, dst_str in FILES_TO_ADD.items():
 src = project_root / src_str
 dst = GITHUB_EXPORT / dst_str
 
 print(f"Preparing: {src_str}")
 
 if prepare_file(src, dst):
 added += 1
 print(f" ✅ Added")
 else:
 failed += 1
 print()
 
 print("=" * 80)
 print(f"✅ Added: {added}")
 print(f"❌ Failed: {failed}")
 print()
 print("Next: Run forensic audit on github_export/")

if __name__ == "__main__":
 main()

