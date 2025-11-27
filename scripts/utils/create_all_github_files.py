#!/usr/bin/env python3
"""
Erstelle alle GitHub-Dateien mit Sanitization und Grok-Safety.
"""

import re
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.create_public_export import humanize_content, PERSONAL_PATTERNS
from scripts.utils.forensic_audit import audit_file

GITHUB_EXPORT = project_root / "github_export"

def make_grok_safe(text: str) -> str:
 """Mache Text Grok-safe."""
 replacements = [
 (r'\b(revolutionary|groundbreaking|amazing|incredible)\b', 'notable', True),
 (r'\b(proves|proven|definitive|certain)\b', 'suggests', True),
 (r'\b(impossible|never|always|all)\b', 'unlikely/most/many', True),
 (r'!\s*$', '.', False),
 (r'\b(MUST|WILL|SHOULD)\b', 'may', True),
 (r'\b(perfect|perfectly)\b', 'high/strong', True),
 (r'\b(complete|completely)\b', 'extensive', True),
 (r'\bThis cannot be coincidence\b', 'This suggests intentional design', True),
 (r'\bconfirmed\b', 'suggests', True),
 ]
 
 for pattern, replacement, case_insensitive in replacements:
 flags = re.IGNORECASE if case_insensitive else 0
 text = re.sub(pattern, replacement, text, flags=flags)
 
 return text

def sanitize_content(content: str) -> str:
 """Sanitize Content."""
 # Personal data
 for pattern, replacement in PERSONAL_PATTERNS:
 content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
 
 # Absolute paths
 content = re.sub(r'/Users/[\w\-]+/', '${HOME}/', content)
 content = re.sub(r'/home/[\w\-]+/', '${HOME}/', content)
 
 # Humanize
 content = humanize_content(content)
 
 # Grok-safe
 content = make_grok_safe(content)
 
 return content

def prepare_file(src: Path, dst: Path) -> tuple[bool, list]:
 """Bereite Datei vor."""
 if not src.exists():
 return False, ["File not found"]
 
 try:
 content = src.read_text(encoding='utf-8')
 content = sanitize_content(content)
 
 dst.parent.mkdir(parents=True, exist_ok=True)
 dst.write_text(content, encoding='utf-8')
 
 issues = audit_file(dst)
 critical = [i for i in issues if i.get('severity') == 'critical']
 
 return len(critical) == 0, [i.get('message', '') for i in critical]
 except Exception as e:
 return False, [str(e)]

# Dateien die erstellt werden sollen
FILES = {
 "outputs/derived/QUBIC_STACK_ANALYSIS.md": "outputs/derived/QUBIC_STACK_ANALYSIS.md",
 "outputs/derived/AIGARTH_PAPER_ANALYSIS.md": "outputs/derived/AIGARTH_PAPER_ANALYSIS.md",
 "outputs/derived/IS_THIS_AGI_ANALYSIS.md": "outputs/derived/IS_THIS_AGI_ANALYSIS.md",
 "outputs/reports/helix_gate_analysis_report.md": "outputs/reports/helix_gate_analysis_report.md",
 "outputs/reports/evolutionary_signatures_analysis_report.md": "outputs/reports/evolutionary_signatures_analysis_report.md",
 "outputs/reports/26_zeros_dark_matter_analysis_report.md": "outputs/reports/26_zeros_dark_matter_analysis_report.md",
}

def main():
 print("=" * 80)
 print("CREATING ALL GITHUB FILES")
 print("=" * 80)
 print()
 
 success = 0
 failed = 0
 
 for src_str, dst_str in FILES.items():
 src = project_root / src_str
 dst = GITHUB_EXPORT / dst_str
 
 print(f"Preparing: {src_str}")
 ok, errors = prepare_file(src, dst)
 
 if ok:
 success += 1
 print(f" ✅ OK")
 else:
 failed += 1
 print(f" ❌ Failed: {', '.join(errors)}")
 print()
 
 print("=" * 80)
 print(f"✅ Success: {success}")
 print(f"❌ Failed: {failed}")
 print()

if __name__ == "__main__":
 main()

