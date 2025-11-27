#!/bin/bash
# Run CFB Discord export with incremental saving

cd ${PROJECT_ROOT:-.}

# Set token (use environment variable or set manually)
# export DISCORD_TOKEN='YOUR_DISCORD_TOKEN_HERE'

# Activate venv if exists
if [ -d "venv-tx" ]; then
    source venv-tx/bin/activate
fi

# Set Python path
export PYTHONPATH=${PROJECT_ROOT:-.}

# Run export
python3 scripts/verify/export_cfb_discord_incremental.py 2>&1 | tee outputs/derived/cfb_discord_messages/export.log

echo ""
echo "Export completed. Check outputs/derived/cfb_discord_messages/"




