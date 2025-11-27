#!/usr/bin/env python3
"""Decode repeating-block clues within the published Base-26 identities."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from analysis.utils.data_loader import ensure_directory
from analysis.utils.identity_tools import IDENTITY_BODY_LENGTH

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "repeating_block_decoder.md"

# Known identities with intentionally invalid checksums (CFB published versions).
# These differ from the valid checksum versions in identity_constants.py
PUBLISHED_IDENTITIES = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRMDCK",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRRDGKC",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLDPHO",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHXMTI",
]

# Mapping derived from community hints.
SHIFT_MAP: Dict[str, int] = {"M": 3, "B": 2, "N": 5, "X": 11}

def _segments(body: str) -> List[str | Tuple[str, int]]:
 """Split an identity body into payload blocks and separator tokens."""

 parts: List[str | Tuple[str, int]] = []
 buffer: List[str] = []
 idx = 0
 n = len(body)
 while idx < n:
 ch = body[idx]
 run = 1
 while idx + run < n and body[idx + run] == ch:
 run += 1
 if run >= 3 and ch in SHIFT_MAP:
 if buffer:
 parts.append("".join(buffer))
 buffer = []
 parts.append((ch, run))
 else:
 buffer.append(ch)
 idx += run
 if buffer:
 parts.append("".join(buffer))
 return parts

def _apply_shift(segment: str, shift: int) -> str:
 if shift == 0:
 return segment
 decoded = []
 for ch in segment:
 value = (ord(ch) - ord("A") - shift) % 26
 decoded.append(chr(ord("A") + value))
 return "".join(decoded)

def decode_identity(identity: str) -> Tuple[str, List[str]]:
 """Return decoded plaintext words and intermediate segments."""

 body = identity[:IDENTITY_BODY_LENGTH]
 decoded_words: List[str] = []
 notes: List[str] = []
 shift = 0

 for part in _segments(body):
 if isinstance(part, tuple):
 marker, run_length = part
 shift = SHIFT_MAP.get(marker, 0)
 notes.append(f"Separator {marker * run_length} → shift {shift}")
 else:
 decoded = _apply_shift(part, shift)
 decoded_words.append(decoded)
 shift = 0
 plaintext = " ".join(decoded_words)
 return plaintext, notes

def write_report(identities: Sequence[str], out_path: Path) -> None:
 ensure_directory(out_path.parent)
 lines: List[str] = [
 "# Repeating-Block Decoder",
 "",
 "Separator rule: `MMM/BBB/NNN/XXX` reset the Caesar shift for the following block.",
 "",
 "| # | Identity | Decoded plaintext | Markers |",
 "| --- | --- | --- | --- |",
 ]

 for idx, identity in enumerate(identities, 1):
 plaintext, notes = decode_identity(identity)
 notes_str = "<br>".join(notes) if notes else "—"
 lines.append(f"| {idx} | `{identity}` | `{plaintext}` | {notes_str} |")

 out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
 write_report(PUBLISHED_IDENTITIES, REPORT_PATH)
 print(f"[repeating-block] ✓ report -> {REPORT_PATH}")

if __name__ == "__main__":
 main()

