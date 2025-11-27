#!/bin/bash
# Resume On-Chain Validation

cd ${PROJECT_ROOT}

echo "=" | tr -d '\n'
for i in {1..80}; do echo -n "="; done
echo
echo "RESUME ON-CHAIN VALIDATION"
echo "=" | tr -d '\n'
for i in {1..80}; do echo -n "="; done
echo
echo

# Check status
echo "Checking current status..."
python3 scripts/core/check_onchain_validation_status.py

echo
echo "Resuming validation..."
python3 scripts/core/onchain_validation_all_identities.py

