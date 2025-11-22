#!/bin/bash
# Final push script - handles pull and push

cd "$(dirname "$0")"

echo "=== Pulling remote changes ==="
git pull origin main --no-rebase

if [ $? -ne 0 ]; then
    echo "✗ Pull failed - checking for conflicts..."
    if [ -f .git/MERGE_HEAD ]; then
        echo "Merge in progress - completing merge..."
        git add -A
        git commit -m "Merge remote changes from origin/main" --no-edit
    fi
fi

echo ""
echo "=== Pushing local commits ==="
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully pushed to GitHub!"
    echo ""
    echo "Summary:"
    git log --oneline -3
else
    echo ""
    echo "✗ Push failed"
    echo "Current status:"
    git status
    exit 1
fi

