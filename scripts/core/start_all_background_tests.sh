#!/bin/bash
# Start All Background Tests

cd "$(dirname "$0")/../.."

echo "=== Starting Background Tests ==="
echo ""

# Check if venv exists
if [ ! -f "venv-tx/bin/python" ]; then
 echo "❌ venv-tx not found!"
 exit 1
fi

echo "✅ venv-tx found"
echo ""

# Create output directory
mkdir -p outputs/derived

# 1. Find Real Seed
echo "Starting: Find Real Seed..."
nohup python3 scripts/core/find_real_seed_using_coordinates.py > outputs/derived/find_real_seed.log 2>&1 &
PID1=$!
echo " ✅ Started (PID: $PID1)"
echo ""

# 2. Compare All Seeds
echo "Starting: Compare All Seeds..."
nohup python3 scripts/core/compare_all_seeds_with_identities.py > outputs/derived/seed_comparison.log 2>&1 &
PID2=$!
echo " ✅ Started (PID: $PID2)"
echo ""

# 3. Smart Contract Scan
echo "Starting: Smart Contract Scan..."
nohup python3 scripts/core/scan_smart_contracts_for_identities.py > outputs/derived/smart_contract_scan.log 2>&1 &
PID3=$!
echo " ✅ Started (PID: $PID3)"
echo ""

# 4. Layer-3 Derivation
echo "Starting: Layer-3 Derivation..."
nohup python3 scripts/core/derive_layer3_complete.py > outputs/derived/layer3_derivation.log 2>&1 &
PID4=$!
echo " ✅ Started (PID: $PID4)"
echo ""

echo "=== All Background Tests Started ==="
echo ""
echo "PIDs:"
echo " Find Real Seed: $PID1"
echo " Compare All Seeds: $PID2"
echo " Smart Contract Scan: $PID3"
echo " Layer-3 Derivation: $PID4"
echo ""
echo "Check status with:"
echo " ps aux | grep -E '$PID1|$PID2|$PID3|$PID4'"
echo ""
echo "Check logs with:"
echo " tail -f outputs/derived/*.log"
echo ""

# Save PIDs
echo "$PID1" > outputs/derived/find_real_seed.pid
echo "$PID2" > outputs/derived/compare_seeds.pid
echo "$PID3" > outputs/derived/smart_contract_scan.pid
echo "$PID4" > outputs/derived/layer3_derivation.pid

echo "✅ PIDs saved to outputs/derived/*.pid"

