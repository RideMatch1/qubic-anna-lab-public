#!/bin/bash
# Script to remove all Unicode characters from run_all_verifications.sh
# and replace them with ASCII equivalents

cd "$(dirname "$0")"

python3 << 'PYEOF'
# Read file completely
with open('run_all_verifications.sh', 'rb') as f:
    content = f.read().decode('utf-8')

# Split into lines
lines = content.split('\n')

# Keep first 360 lines
new_lines = lines[:360]

# Replace ALL Unicode characters in all lines
unicode_replacements = {
    '━': '-',
    '✓': '[OK]',
    '✗': '[ERROR]',
    '⚠': '[WARNING]',
    '✅': '[OK]',
    '📁': '[FOLDER]'
}

for i in range(len(new_lines)):
    for unicode_char, replacement in unicode_replacements.items():
        new_lines[i] = new_lines[i].replace(unicode_char, replacement)

# Add clean ending (NO Unicode)
new_lines.append('')
new_lines.append('echo ""')
new_lines.append('echo "For more information, see:"')
new_lines.append('echo "  - verification_complete.txt (verification summary)"')
new_lines.append('echo "  - FOUND_IDENTITIES.md (8 initial identities)"')
new_lines.append('echo "  - outputs/reports/ (detailed analysis reports)"')
new_lines.append('if [ -n "$DESKTOP_DIR" ]; then')
new_lines.append('    echo "  - Desktop folder: $DESKTOP_DIR (organized results)"')
new_lines.append('fi')
new_lines.append('echo ""')

# Write back
with open('run_all_verifications.sh', 'wb') as f:
    f.write('\n'.join(new_lines).encode('utf-8'))

print(f"✓ Script fixed! {len(new_lines)} lines, all Unicode removed")
PYEOF

# Validate syntax
if bash -n run_all_verifications.sh 2>/dev/null; then
    echo "✓ Syntax validated!"
    chmod +x run_all_verifications.sh
    echo "✓ File is executable"
    echo ""
    echo "Summary:"
    wc -l run_all_verifications.sh
    echo ""
    echo "Last 10 lines:"
    tail -10 run_all_verifications.sh
else
    echo "✗ Syntax error detected!"
    exit 1
fi

