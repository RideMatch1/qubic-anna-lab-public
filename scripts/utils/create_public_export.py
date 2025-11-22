#!/usr/bin/env python3
"""
Create public GitHub export - filtered and sanitized

Filters out:
- Genesis/contract/transaction strategies
- Personal data
- LLM-typical formulations
- Internal research steps
- Sensitive findings

Keeps:
- Core discovery (8 identities from matrix)
- On-chain verification
- Basic layer structure (Layer-1 → Layer-2)
- Reproducible extraction methods
- Statistical proof
"""

import re
import shutil
from pathlib import Path
from typing import List, Set

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXPORT_DIR = PROJECT_ROOT / "github_export"

# Files to exclude completely
EXCLUDE_FILES = [
    "outputs/derived/",  # Wird selektiv über include_dirs eingefügt
    "venv/",
    "venv-tx/",
    "__pycache__/",
    ".git/",
    "github_export/",
    "*.log",
    "*.tmp",
    "*.checkpoint.json",
    "*_checkpoint.json",
    "outputs/reports/*.json",
    "outputs/reports/*.csv",
    "outputs/derived/cfb_discord_messages/",
    "outputs/derived/*.json",  # JSON-Dateien ausschließen (nur Reports)
    "repos/",
    "DiscordChatExporter*",
    "client/",
    "qubic-cli/",
    "data/computor-data/",
    # Interne Strategie-Dokumente (nicht öffentlich)
    "outputs/derived/*STRATEGY*.md",
    "outputs/derived/*MASTER*.md",
    "outputs/derived/*CONTRACT*.md",
    "outputs/derived/*DISCORD*.md",
    "outputs/derived/*BREAKTHROUGH*.md",
    "outputs/derived/*FUSION*.md",
    "outputs/derived/*WALLET*.md",
    "outputs/derived/*ASSET*.md",
    "outputs/derived/*TRANSACTION*.md",
    "outputs/derived/*BLOCK*.md",
    "outputs/derived/*TICK*.md",
    "outputs/derived/*LAYER3*.md",
    "outputs/derived/*LAYER4*.md",
    "outputs/derived/*LAYER5*.md",
    "outputs/derived/*DEEP_LAYER*.md",
    "outputs/derived/*COMPLETE_LAYER*.md",
]

# Files that contain Genesis/contract strategies (exclude)
GENESIS_STRATEGY_FILES = [
    "scripts/verify/smart_contract_test*.py",
    "scripts/verify/test_*.py",
    "scripts/verify/brute_force*.py",
    "scripts/verify/final_contract*.py",
    "scripts/verify/phase2_contract*.py",
    "scripts/core/send_from_real_layer2*.py",
    "scripts/core/master_seed_fusion*.py",
    "scripts/verify/*.md",  # Strategy docs
    "scripts/verify/analyze_cfb*.py",
    "scripts/verify/export_cfb*.py",
    "scripts/verify/discord_intelligence*.py",
    "scripts/verify/qubictrade*.py",
    "scripts/verify/asset_monitor.py",
    "scripts/verify/block_sniffer*.py",
    "scripts/verify/complete_layer_map.py",
    "scripts/verify/deep_layer_exploration.py",
    "scripts/verify/layer3_analysis.py",
]

# Patterns to remove from content (Genesis/contract related)
GENESIS_PATTERNS = [
    r"genesis|Genesis|GENESIS",
    r"contract.*trigger|trigger.*contract",
    r"smart contract",
    r"transaction.*payload|payload.*transaction",
    r"tick.*gap|gap.*tick",
    r"Block-ID|Block ID",
    r"Layer-Index",
    r"reward|Reward|prize|Prize|schatz|Schatz|treasure",
    r"24,696|24,720|outgoing.*transaction",
    r"QubicTrade|qubictrade",
    r"GENESIS.*asset|asset.*GENESIS",
    r"IPO.*payout",
    r"vend machine",
    r"claim.*data",
]

# LLM-typical phrases to remove/make human
LLM_PHRASES = [
    (r"Let me ", "I'll "),
    (r"Let's ", ""),
    (r"Here's ", ""),
    (r"Here are ", ""),
    (r"Note that ", ""),
    (r"Please note ", ""),
    (r"It's important to ", ""),
    (r"Keep in mind that ", ""),
    (r"Make sure to ", ""),
    (r"Don't forget to ", ""),
    (r"Remember to ", ""),
    (r"Be sure to ", ""),
    (r"Feel free to ", ""),
    (r"As you can see", ""),
    (r"As we can see", ""),
    (r"In this case", ""),
    (r"In other words", ""),
    (r"To put it simply", ""),
    (r"To summarize", ""),
    (r"In summary", ""),
    (r"To conclude", ""),
    (r"First and foremost", "First"),
    (r"Last but not least", "Finally"),
    (r"Needless to say", ""),
    (r"It goes without saying", ""),
    (r"With that said", ""),
    (r"That being said", ""),
    (r"Having said that", ""),
]

# Personal data patterns (these are used for sanitization, not actual data leaks)
PERSONAL_PATTERNS = [
    (r"/Users/[\w\-]+/", "${PROJECT_ROOT}"),
    (r"/Users/[\w\-]+/projects/[\w\-]+", "${PROJECT_ROOT}"),
    (r"[\w\-]+", "user"),  # Generic username pattern
    (r"[A-Z][a-z]+\s+[A-Z][a-z]+", "Researcher"),  # Generic "First Last" pattern
    (r"/tmp/", "${TMPDIR:-/tmp}/"),
]

def should_exclude(file_path: Path) -> bool:
    """Check if file should be excluded."""
    rel_path = str(file_path.relative_to(PROJECT_ROOT))
    for pattern in EXCLUDE_FILES:
        if pattern in rel_path or file_path.match(pattern):
            return True
    return False

def is_genesis_strategy_file(file_path: Path) -> bool:
    """Check if file contains Genesis/contract strategies."""
    rel_path = str(file_path.relative_to(PROJECT_ROOT))
    for pattern in GENESIS_STRATEGY_FILES:
        if file_path.match(pattern) or pattern in rel_path:
            return True
    return False

def contains_genesis_content(content: str) -> bool:
    """Check if content contains Genesis/contract strategies."""
    content_lower = content.lower()
    for pattern in GENESIS_PATTERNS:
        if re.search(pattern, content_lower):
            return True
    return False

def humanize_content(content: str) -> str:
    """Remove LLM-typical phrases, make it more human."""
    result = content
    
    # Remove LLM phrases
    for pattern, replacement in LLM_PHRASES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Remove personal data
    for pattern, replacement in PERSONAL_PATTERNS:
        result = re.sub(pattern, replacement, result)
    
    # Remove Genesis-related sections (entire paragraphs)
    lines = result.split('\n')
    filtered_lines = []
    skip_until_empty = False
    
    for line in lines:
        if contains_genesis_content(line):
            skip_until_empty = True
            continue
        if skip_until_empty and line.strip() == '':
            skip_until_empty = False
            continue
        if not skip_until_empty:
            filtered_lines.append(line)
    
    result = '\n'.join(filtered_lines)
    
    # Clean up multiple empty lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result

def sanitize_file(src: Path, dst: Path):
    """Sanitize file content."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        content = src.read_text(encoding='utf-8', errors='ignore')
        
        # Skip if contains Genesis strategies
        if contains_genesis_content(content) and src.suffix in ['.md', '.py']:
            # For Python files, try to remove only Genesis-related functions
            if src.suffix == '.py':
                # Remove functions with Genesis in name or docstring
                lines = content.split('\n')
                filtered_lines = []
                skip_function = False
                indent_level = 0
                
                for line in lines:
                    # Check if function definition contains Genesis
                    if re.match(r'^\s*def\s+.*genesis', line, re.IGNORECASE):
                        skip_function = True
                        indent_level = len(line) - len(line.lstrip())
                        continue
                    
                    # Check if we're still in the function
                    if skip_function:
                        current_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level
                        if line.strip() == '' or current_indent > indent_level:
                            continue
                        else:
                            skip_function = False
                    
                    filtered_lines.append(line)
                
                content = '\n'.join(filtered_lines)
            else:
                # For markdown, just skip the file
                return
        
        # Humanize content
        sanitized = humanize_content(content)
        
        # Additional Python-specific sanitization
        if src.suffix == '.py':
            # Replace absolute paths in code
            sanitized = re.sub(
                r'Path\(["\']/Users/[\w\-]+/',
                r'Path(__file__).parent.parent.parent / ',
                sanitized
            )
            # Replace cd commands in comments
            sanitized = re.sub(
                r'cd /Users/[\w\-]+/projects/',
                r'cd ${PROJECT_ROOT}',
                sanitized
            )
        
        dst.write_text(sanitized, encoding='utf-8')
        print(f"  ✓ {src.relative_to(PROJECT_ROOT)}")
        
    except Exception as e:
        print(f"  ✗ {src.relative_to(PROJECT_ROOT)}: {e}")

def export_public_repo():
    """Export public repository."""
    print("=" * 80)
    print("CREATING PUBLIC GITHUB EXPORT")
    print("=" * 80)
    print()
    print("Filtering:")
    print("  - Contract strategies")
    print("  - Personal data")
    print("  - LLM-typical phrases")
    print("  - Internal research steps")
    print()
    
    # Remove old export
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    files_copied = 0
    files_excluded = 0
    files_sanitized = 0
    
    # Core files to include
    core_files = [
        "README.md",
        "PROOF_OF_WORK.md",
        "requirements.txt",
        "Dockerfile.qubipy",
        ".gitignore",
        "data/anna-matrix/Anna_Matrix.xlsx",
    ]
    
    # Directories to include
    include_dirs = [
        "analysis/",
        "scripts/core/standardized_conversion.py",
        "scripts/core/seed_candidate_scan.py",
        "scripts/verify/rpc_check.py",
        "scripts/verify/control_group.py",
        "scripts/verify/identity_deep_scan.py",
        "scripts/verify/ping.py",
        "outputs/reports/base26_identity_report.md",
        "outputs/reports/9_vortex_identity_report.md",
        "outputs/reports/control_group_report.md",
        "outputs/reports/seed_candidate_scan.md",
        "outputs/reports/qubipy_identity_check.md",
        # Neue öffentlich relevante Analysen (nur Fakten, keine Strategien)
        "outputs/derived/matrix_origin_analysis_report.md",
        "outputs/derived/missing_layer2_analysis_report.md",
        "outputs/derived/matrix_value_correlation_report.md",
        "outputs/derived/mathematical_properties_analysis_report.md",
        "outputs/derived/identity_pattern_comparison_report.md",
        "outputs/derived/deep_pattern_analysis_report.md",
        "outputs/derived/matrix_coordinate_deep_analysis_report.md",
        "outputs/derived/critical_validation_report.md",
        "outputs/derived/comprehensive_scan_identities_analysis_report.md",
        "outputs/derived/comprehensive_scan_layer2_derivation_report.md",
        "outputs/derived/checkpoint_data_analysis_report.md",
        "docs/",
    ]
    
    # Copy core files
    for file_pattern in core_files:
        src = PROJECT_ROOT / file_pattern
        if src.exists():
            if src.is_file():
                dst = EXPORT_DIR / file_pattern
                sanitize_file(src, dst)
                files_copied += 1
            else:
                # Directory
                for file_path in src.rglob('*'):
                    if file_path.is_file() and not should_exclude(file_path):
                        rel_path = file_path.relative_to(PROJECT_ROOT)
                        dst = EXPORT_DIR / rel_path
                        sanitize_file(file_path, dst)
                        files_copied += 1
    
    # Copy include directories/files
    for pattern in include_dirs:
        src = PROJECT_ROOT / pattern
        if src.exists():
            if src.is_file():
                if not is_genesis_strategy_file(src):
                    dst = EXPORT_DIR / pattern
                    sanitize_file(src, dst)
                    files_copied += 1
                else:
                    files_excluded += 1
            else:
                for file_path in src.rglob('*'):
                    if file_path.is_file() and not should_exclude(file_path):
                        if not is_genesis_strategy_file(file_path):
                            sanitize_file(file_path, EXPORT_DIR / file_path.relative_to(PROJECT_ROOT))
                            files_copied += 1
                        else:
                            files_excluded += 1
    
    # Copy scripts/utils (forensic_audit for verification)
    utils_dir = PROJECT_ROOT / "scripts" / "utils"
    if utils_dir.exists():
        for file_path in utils_dir.rglob('*.py'):
            if file_path.name in ['forensic_audit.py', 'create_public_export.py']:
                dst = EXPORT_DIR / file_path.relative_to(PROJECT_ROOT)
                sanitize_file(file_path, dst)
                files_copied += 1
    
    print()
    print("=" * 80)
    print("EXPORT SUMMARY")
    print("=" * 80)
    print(f"Files copied: {files_copied}")
    print(f"Files excluded (Genesis/contract): {files_excluded}")
    print(f"Export directory: {EXPORT_DIR}")
    print()
    print("Next steps:")
    print("1. Review: cd github_export && ls -la")
    print("2. Test: python3 scripts/utils/forensic_audit.py")
    print("3. Verify: Check that no Genesis strategies leaked")
    print("4. Commit: git add . && git commit -m 'Public release'")

if __name__ == "__main__":
    export_public_repo()

