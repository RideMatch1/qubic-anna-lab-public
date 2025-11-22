#!/bin/bash
# Fix Git merge issues and ensure correct matrix file
# Run this from the repository root directory

set -e

# Get script directory (repository root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Fixing Git merge and matrix file ==="

# 1. Abort any unfinished merge
echo "1. Aborting unfinished merge..."
git merge --abort 2>/dev/null || echo "   No merge to abort"

# 2. Ensure correct matrix file
echo "2. Ensuring correct matrix file..."
# Note: This assumes the matrix file exists in the expected location
# If it doesn't, the hash check below will fail
if [ -f "data/anna-matrix/Anna_Matrix.xlsx" ]; then
    echo "   Matrix file found in repository"
else
    echo "   ⚠️  Matrix file not found - ensure data/anna-matrix/Anna_Matrix.xlsx exists"
    exit 1
fi
HASH=$(shasum -a 256 data/anna-matrix/Anna_Matrix.xlsx | cut -d' ' -f1)
EXPECTED="bdee333b4006c1b7ab24a0dc61de76b60210c2db7bd8822c50e8509aff907c45"

if [ "$HASH" = "$EXPECTED" ]; then
    echo "   ✅ Matrix file hash correct: $HASH"
else
    echo "   ❌ Matrix file hash wrong: $HASH (expected: $EXPECTED)"
    exit 1
fi

# 3. Add and commit
echo "3. Staging changes..."
git add -A
git add data/anna-matrix/Anna_Matrix.xlsx

echo "4. Committing..."
git commit -m "Fix: Ensure correct matrix file

- SHA256: bdee333b4006c1b7ab24a0dc61de76b60210c2db7bd8822c50e8509aff907c45" || echo "   No changes to commit"

# 5. Pull with rebase
echo "5. Pulling remote changes..."
git pull origin main --rebase || {
    echo "   Rebase failed, trying merge..."
    git pull origin main --no-rebase || {
        echo "   Merge failed, forcing push..."
        git push --force origin main
        exit 0
    }
}

# 6. Check matrix file again after pull
HASH_AFTER=$(shasum -a 256 data/anna-matrix/Anna_Matrix.xlsx | cut -d' ' -f1)
if [ "$HASH_AFTER" != "$EXPECTED" ]; then
    echo "6. Matrix file wrong after pull, fixing..."
    cp ../data/anna-matrix/Anna_Matrix.xlsx data/anna-matrix/Anna_Matrix.xlsx
    git add data/anna-matrix/Anna_Matrix.xlsx
    git commit -m "Fix: Restore correct matrix file after pull"
fi

# 7. Push
echo "7. Pushing to remote..."
git push origin main

echo ""
echo "=== Done! ==="
echo "Matrix file hash: $(shasum -a 256 data/anna-matrix/Anna_Matrix.xlsx | cut -d' ' -f1)"
echo "Expected: $EXPECTED"

