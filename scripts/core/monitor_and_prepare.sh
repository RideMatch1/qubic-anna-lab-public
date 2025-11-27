#!/bin/bash
# Monitor On-Chain Validierung und bereite Auswertungen vor

cd "$(dirname "$0")/../.."

echo "=========================================="
echo "MONITOR & PREPARE SCRIPT"
echo "=========================================="
echo ""

# Check ob Validierung läuft
if ps aux | grep -q "[v]alidate_checksum_identities_batch_optimized"; then
 echo "✅ On-chain validation is RUNNING"
 echo ""
 echo "Current progress:"
 python3 scripts/core/monitor_progress.py 2>&1 | grep -A 5 "ON-CHAIN"
else
 echo "⏸️ On-chain validation is NOT running"
 echo ""
 echo "Checking if complete..."
 
 # Check ob komplett
 if python3 -c "import json; from pathlib import Path; cp = Path('outputs/derived/onchain_validation_checkpoint.json'); data = json.load(cp.open()) if cp.exists() else {}; processed = data.get('processed', 0); print('Progress:', processed, '/ 23765 (', processed/23765*100, '%)')" 2>/dev/null | grep -q "100"; then
 echo "✅ Validation is COMPLETE"
 echo ""
 echo "Preparing final analysis..."
 python3 scripts/core/prepare_final_analysis.py
 echo ""
 echo "Creating comprehensive summary..."
 python3 scripts/core/create_comprehensive_summary.py
 else
 echo "⚠️ Validation is INCOMPLETE"
 echo ""
 echo "To resume:"
 echo " python3 scripts/core/validate_checksum_identities_batch_optimized.py --resume"
 fi
fi

echo ""
echo "=========================================="

