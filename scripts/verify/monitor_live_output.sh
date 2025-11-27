#!/bin/bash
# Monitor Live Output from both scripts

cd ${PROJECT_ROOT}

echo "=========================================="
echo "LIVE MONITORING: Mass Seed Derivation & Contract TX Extraction"
echo "=========================================="
echo ""

# Function to show last N lines from a log file
show_log() {
 local file=$1
 local name=$2
 if [ -f "$file" ]; then
 echo "=== $name ==="
 tail -5 "$file" 2>/dev/null | sed 's/^/ /'
 echo ""
 else
 echo "=== $name ==="
 echo " (No output yet)"
 echo ""
 fi
}

# Monitor loop
while true; do
 clear
 echo "=========================================="
 echo "LIVE MONITORING (Updated every 5 seconds)"
 echo "Press Ctrl+C to stop"
 echo "=========================================="
 echo ""
 
 show_log "outputs/derived/mass_seed_derivation_live.log" "MASS SEED DERIVATION"
 show_log "outputs/derived/contract_tx_extraction_live.log" "CONTRACT TX EXTRACTION"
 
 echo "=========================================="
 echo "Last update: $(date '+%H:%M:%S')"
 echo "=========================================="
 
 sleep 5
done

