#!/bin/bash
# Run Master Seed Fusion with Docker (QubiPy)

cd ${PROJECT_ROOT}

docker run --rm \
 -v "$PWD":/workspace \
 -w /workspace \
 -e PYTHONPATH=/workspace \
 qubic-proof \
 python3 scripts/core/master_seed_fusion.py

