#!/bin/bash
# Organize repository files - Complete cleanup

cd "$(dirname "$0")"

# Create directories
mkdir -p docs/status docs/internal outputs/analysis

echo "Organizing repository files..."

# Move status files
echo "Moving status files..."
for f in ALL_FILES_UPDATED.md ALL_UPDATES_COMPLETE.md COMMIT_READY.md COMMIT_STATUS.md FINAL_GITHUB_CHECK.md FINAL_UPDATE_SUMMARY.md GITHUB_UPDATE_COMPLETE.md UPDATE_COMPLETE.md; do
    [ -f "$f" ] && mv "$f" docs/status/ && echo "  Moved $f to docs/status/"
done

# Move internal files
echo "Moving internal files..."
for f in VALIDATION_REPORT.md VALIDATION_COMPLETE.md VALIDATED_SEEDS_WITH_PRIVATE_KEYS.md AUDIT_REPORT.md CRITICAL_AUDIT_REPORT.md FIXES_SUMMARY.md GIT_COMMIT_INSTRUCTIONS.md READY_FOR_GITHUB.md REPRODUCIBILITY_CHECK.md SIGNED_MESSAGE_PROOF.md WHAT_WE_FOUND_VS_WHAT_WE_CREATED.md COMMIT_MESSAGE.txt MONTE_CARLO_STATUS.md; do
    [ -f "$f" ] && mv "$f" docs/internal/ && echo "  Moved $f to docs/internal/"
done

# Move log files
echo "Moving log files..."
for f in monte_carlo_output.log monte_carlo_run.log; do
    [ -f "$f" ] && mv "$f" docs/internal/ && echo "  Moved $f to docs/internal/"
done

# Copy mapping database if it exists
if [ -f "../outputs/analysis/complete_mapping_database.json" ]; then
    cp ../outputs/analysis/complete_mapping_database.json outputs/analysis/
    echo "  Copied mapping database to outputs/analysis/"
fi

echo ""
echo "Organization complete!"
echo ""
echo "Root level MD files:"
ls -1 *.md 2>/dev/null | wc -l
echo ""
echo "Files moved to docs/status/:"
ls -1 docs/status/*.md 2>/dev/null | wc -l
echo ""
echo "Files moved to docs/internal/:"
ls -1 docs/internal/*.md docs/internal/*.txt docs/internal/*.log 2>/dev/null | wc -l
