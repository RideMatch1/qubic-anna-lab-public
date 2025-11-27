#!/bin/bash
# Background script to export CFB Discord messages

cd ${PROJECT_ROOT}

# Activate venv if exists
if [ -d "venv-tx" ]; then
 source venv-tx/bin/activate
fi

# Set Python path
export PYTHONPATH=${PROJECT_ROOT}

# Run export script
python3 scripts/verify/export_cfb_discord_fast.py > outputs/derived/cfb_discord_messages/export.log 2>&1

echo "Export completed. Check outputs/derived/cfb_discord_messages/"

