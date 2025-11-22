#!/bin/bash
# Script to pull remote changes and push local commits

cd "$(dirname "$0")"

echo "=== Pulling remote changes ==="
git pull origin main --no-rebase

if [ $? -ne 0 ]; then
    echo "✗ Pull failed - there may be merge conflicts"
    echo "Please resolve conflicts manually and then run:"
    echo "  git add -A"
    echo "  git commit -m 'Merge remote changes'"
    echo "  git push origin main"
    exit 1
fi

echo ""
echo "=== Pushing local commits ==="
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully pushed to GitHub!"
else
    echo ""
    echo "✗ Push failed"
    exit 1
fi

