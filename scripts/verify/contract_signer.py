#!/usr/bin/env python3
"""
Contract Signer
---------------

Signs a given message with every seed-derived identity from the Anna Matrix.

- Default message references the Anna Matrix hash and the mysterious asset issuer
 (POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD).
- Seeds are loaded from outputs/derived/identity_deep_scan.json if available;
 otherwise they are recomputed from the diagonal/vortex identities.
- Produces JSON + Markdown files with signatures for sharing (e.g., Discord proof).

Usage:
 python scripts/verify/contract_signer.py --message "Custom message"
"""

from __future__ import annotations

import argparse
import base64
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

import ed25519

from scripts.core.seed_candidate_scan import (
 DIAGONAL_IDENTITIES,
 VORTEX_IDENTITIES,
 derive_identity_from_seed,
)

DEFAULT_MESSAGE = (
 "AnnaMatrix|6006c6650a9dab69901a9420a7dbd64703d7f6849ff95300677160c9f193ca6d|"
 "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
)

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "contract_signatures.json"
OUTPUT_MD = OUTPUT_DIR / "contract_signatures.md"
IDENTITY_BODY_LEN = 56
SEED_LEN = 55

def seed_from_identity(identity: str) -> str:
 body = identity[:IDENTITY_BODY_LEN]
 return body.lower()[:SEED_LEN]

def load_seeds_from_inventory() -> List[dict]:
 inventory = OUTPUT_DIR / "identity_deep_scan.json"
 if not inventory.exists():
 return []
 data = json.loads(inventory.read_text())
 seeds = []
 for record in data.get("records", []):
 seed = record.get("seed")
 identity = record.get("identity")
 label = record.get("label")
 if seed and identity and label and "Layer-2" in label:
 seeds.append({"label": label, "seed": seed, "identity": identity})
 return seeds

def recompute_layer2_seeds() -> List[dict]:
 seeds = []
 def append(prefix: str, identities: List[str]) -> None:
 for idx, identity in enumerate(identities, 1):
 seed = seed_from_identity(identity)
 derived = derive_identity_from_seed(seed)
 if derived:
 seeds.append(
 {"label": f"{prefix} #{idx} • Layer-2", "seed": seed, "identity": derived}
 )
 append("Diagonal", DIAGONAL_IDENTITIES)
 append("Vortex", VORTEX_IDENTITIES)
 return seeds

@dataclass
class SignatureRecord:
 label: str
 identity: str
 seed: str
 signature_hex: str
 signature_b64: str
 message: str

def sign_message(seed: str, message: bytes) -> bytes:
 # Qubic seeds are 55 lowercase letters; derive 32 bytes via SHA-256
 import hashlib

 seed_bytes = hashlib.sha256(seed.encode("utf-8")).digest()
 private_key = ed25519.SigningKey(seed_bytes)
 return private_key.sign(message)

def main() -> None:
 parser = argparse.ArgumentParser(description="Sign a message with all Layer-2 seeds.")
 parser.add_argument("--message", default=DEFAULT_MESSAGE, help="Message to sign")
 args = parser.parse_args()
 message = args.message.encode("utf-8")

 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 seeds = load_seeds_from_inventory() or recompute_layer2_seeds()
 if not seeds:
 raise SystemExit("No seeds available. Run identity_deep_scan first.")

 records: List[SignatureRecord] = []
 for entry in seeds:
 signature = sign_message(entry["seed"], message)
 records.append(
 SignatureRecord(
 label=entry["label"],
 identity=entry["identity"],
 seed=entry["seed"],
 signature_hex=signature.hex(),
 signature_b64=base64.b64encode(signature).decode(),
 message=args.message,
 )
 )

 OUTPUT_JSON.write_text(json.dumps([asdict(r) for r in records], indent=2), encoding="utf-8")

 lines = [
 "# Contract Signatures",
 "",
 f"- Message: `{args.message}`",
 f"- Total signatures: {len(records)}",
 "",
 "| Label | Identity | Seed | Signature (hex) |",
 "| --- | --- | --- | --- |",
 ]

 for record in records:
 lines.append(
 f"| {record.label} | `{record.identity}` | `{record.seed}` | `{record.signature_hex}` |"
 )

 lines.extend(["", "## Signature Details", ""])
 for record in records:
 lines.extend(
 [
 f"### {record.label}",
 "",
 f"- Identity: `{record.identity}`",
 f"- Seed: `{record.seed}`",
 f"- Signature (hex): `{record.signature_hex}`",
 f"- Signature (base64): `{record.signature_b64}`",
 "",
 ]
 )

 OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
 print(f"[contract-signer] ✓ json -> {OUTPUT_JSON}")
 print(f"[contract-signer] ✓ markdown -> {OUTPUT_MD}")

if __name__ == "__main__":
 main()

