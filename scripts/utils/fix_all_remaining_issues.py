#!/usr/bin/env python3
"""
Fix all remaining issues: local paths, German comments, LLM bias
"""

import re
import sys
from pathlib import Path

# Path replacements
PATH_REPLACEMENTS = [
    (r'\$\{PROJECTS_ROOT\}/qubic-anna-lab-clean', '${DISCORD_EXPORTER_DIR}'),
    (r'/Users/lukashertle/projects/qubic-mystery-lab', '${PROJECT_ROOT}'),
    (r'/Users/lukashertle/projects', '${PROJECTS_ROOT}'),
    (r'lukashertle', '${USER}'),
]

# German to English translations
GERMAN_REPLACEMENTS = [
    (r'Validiere', 'Validate'),
    (r'validiere', 'validate'),
    (r'Analysiere', 'Analyze'),
    (r'analysiere', 'analyze'),
    (r'Prüfe', 'Check'),
    (r'prüfe', 'check'),
    (r'für', 'for'),
    (r'über Zufall', 'above random'),
    (r'über', 'above'),
    (r'wird', 'will'),
    (r'Wird', 'Will'),
    (r'Lade', 'Load'),
    (r'lade', 'load'),
    (r'Pfade', 'Paths'),
    (r'pfade', 'paths'),
    (r'Kontext', 'context'),
    (r'kontext', 'context'),
]

# LLM bias phrases
LLM_REPLACEMENTS = [
    (r'\bLet me\b', ''),
    (r'\bI am an AI\b', ''),
    (r'\bI can help\b', ''),
    (r'\bI would like\b', ''),
    (r'\bI think\b', ''),
    (r'\bI believe\b', ''),
]

def fix_file(filepath: Path) -> bool:
    """Fix issues in a single file. Returns True if changed."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        original = content
        
        # Apply path replacements
        for pattern, replacement in PATH_REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # Apply German replacements
        for pattern, replacement in GERMAN_REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # Apply LLM replacements
        for pattern, replacement in LLM_REPLACEMENTS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Clean up
        content = re.sub(r' +', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Process all code files."""
    repo_root = Path(__file__).parent.parent.parent
    
    # File types to process
    extensions = ['.py', '.sh']
    
    files_to_process = []
    for ext in extensions:
        files_to_process.extend(repo_root.rglob(f'*{ext}'))
    
    # Filter out .git and utils scripts
    files_to_process = [
        f for f in files_to_process
        if '.git' not in str(f) 
        and 'node_modules' not in str(f)
        and 'fix_all' not in str(f)
    ]
    
    print(f"Processing {len(files_to_process)} files...")
    
    fixed_count = 0
    for filepath in files_to_process:
        if fix_file(filepath):
            fixed_count += 1
            print(f"Fixed: {filepath.relative_to(repo_root)}")
    
    print(f"\nFixed {fixed_count} files.")

if __name__ == '__main__':
    main()

