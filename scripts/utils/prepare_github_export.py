#!/usr/bin/env python3
"""
Prepare clean export for GitHub upload.

This script creates a sanitized copy of the repository without modifying
the original files. It removes sensitive data and prepares files for
public GitHub upload.

IMPORTANT: This does NOT modify the original repository!
"""

import re
import shutil
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXPORT_DIR = PROJECT_ROOT / "github_export"

# Files/directories to exclude from export
EXCLUDE_PATTERNS = [
 ".git/",
 "venv/",
 "venv-tx/",
 "__pycache__/",
 ".DS_Store",
 "*.pyc",
 "*.pyo",
 "*.pyd",
 "github_export/",
 "outputs/derived/",
 "outputs/reports/*.json",
 "outputs/reports/*.csv",
 "outputs/reports/*.log",
 "*.log",
 "*.tmp",
 "repos/",
 "DiscordChatExporter*",
 "client/",
 "qubic-cli/",
 "data/computor-data/",
 "*.ipynb_checkpoints/",
]

# Files that need sanitization (replacements)
SANITIZE_FILES = [
 "scripts/core/resume_onchain_validation.sh",
 "scripts/core/check_onchain_validation_status.py",
 "scripts/core/check_scan_status.py",
 "scripts/verify/monitor_live_output.sh",
 "scripts/verify/run_cfb_export_*.sh",
 "scripts/verify/export_cfb_*.py",
 "Dockerfile.qubipy",
]

# Replacement patterns
REPLACEMENTS = [
 # Absolute paths
 (r"${PROJECT_ROOT}", "${PROJECT_ROOT}"),
 (r"${DISCORD_EXPORTER_DIR}", "${PROJECT_ROOT}"),
 (r"/tmp/", "${TMPDIR:-/tmp}/"),
 # Personal names
 (r"${USER}", "user"),
 (r"Lukas Hertle", "Researcher"),
 # Keep Qubic node IPs (they're public)
]

def should_exclude(file_path: Path) -> bool:
 """Check if file should be excluded."""
 path_str = str(file_path.relative_to(PROJECT_ROOT))
 for pattern in EXCLUDE_PATTERNS:
 if pattern in path_str or file_path.match(pattern):
 return True
 return False

def sanitize_content(content: str, file_path: Path) -> str:
 """Sanitize file content."""
 result = content
 
 # Apply replacements
 for pattern, replacement in REPLACEMENTS:
 result = re.sub(pattern, replacement, result)
 
 # Special handling for shell scripts
 if file_path.suffix == '.sh':
 # Replace cd commands with relative paths
 result = re.sub(
 r'cd ${PROJECT_ROOT}',
 'cd "$(dirname "$0")/../.."',
 result
 )
 
 return result

def needs_sanitization(file_path: Path) -> bool:
 """Check if file needs sanitization."""
 rel_path = str(file_path.relative_to(PROJECT_ROOT))
 for pattern in SANITIZE_FILES:
 if file_path.match(pattern) or pattern in rel_path:
 return True
 return False

def copy_file(src: Path, dst: Path):
 """Copy file with optional sanitization."""
 dst.parent.mkdir(parents=True, exist_ok=True)
 
 if needs_sanitization(src):
 # Read, sanitize, write
 content = src.read_text(encoding='utf-8', errors='ignore')
 sanitized = sanitize_content(content, src)
 dst.write_text(sanitized, encoding='utf-8')
 print(f" Sanitized: {src.relative_to(PROJECT_ROOT)}")
 else:
 # Direct copy
 shutil.copy2(src, dst)

def export_repository():
 """Export repository to clean directory."""
 print("=" * 80)
 print("GITHUB EXPORT PREPARATION")
 print("=" * 80)
 print()
 
 # Remove old export if exists
 if EXPORT_DIR.exists():
 print(f"Removing old export directory: {EXPORT_DIR}")
 shutil.rmtree(EXPORT_DIR)
 
 EXPORT_DIR.mkdir(parents=True, exist_ok=True)
 
 # Copy files
 files_copied = 0
 files_sanitized = 0
 
 for file_path in PROJECT_ROOT.rglob('*'):
 if file_path.is_file() and not should_exclude(file_path):
 rel_path = file_path.relative_to(PROJECT_ROOT)
 dst_path = EXPORT_DIR / rel_path
 
 copy_file(file_path, dst_path)
 files_copied += 1
 
 if needs_sanitization(file_path):
 files_sanitized += 1
 
 print()
 print("=" * 80)
 print("EXPORT SUMMARY")
 print("=" * 80)
 print(f"Files copied: {files_copied}")
 print(f"Files sanitized: {files_sanitized}")
 print(f"Export directory: {EXPORT_DIR}")
 print()
 print("Next steps:")
 print("1. Review exported files in: github_export/")
 print("2. Run forensic audit on export: python3 scripts/utils/forensic_audit.py")
 print("3. Test that everything works")
 print("4. Commit and push to GitHub")

if __name__ == "__main__":
 export_repository()

