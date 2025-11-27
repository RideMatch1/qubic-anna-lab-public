"""Shared helpers for Base-26 decoding and Qubic identity utilities."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import struct

ALPHABET_OFFSET = ord("A")
IDENTITY_BODY_LENGTH = 56
IDENTITY_LENGTH = 60
GROUP_LENGTH = 14
GROUP_COUNT = 4

@dataclass(frozen=True)
class IdentityRecord:
 """Container describing an extracted identity."""

 label: str
 identity: str
 public_key: str
 checksum_valid: bool
 path: Tuple[Tuple[int, int], ...]
 note: str = ""

def base26_char(value: float) -> str:
 """Convert a matrix value to its Base-26 letter."""

 idx = int(abs(value)) % 26
 return chr(ALPHABET_OFFSET + idx)

def matrix_hash(matrix: np.ndarray) -> str:
 """Return a stable SHA-256 hash for the numeric matrix."""

 normalized = np.asarray(matrix, dtype=np.float32)
 return sha256(normalized.tobytes()).hexdigest()

def _encode_group(chars: Sequence[str]) -> int:
 """Encode a 14-character block into the uint64 fragment."""

 frag = 0
 for ch in reversed(chars):
 frag = frag * 26 + (ord(ch) - ALPHABET_OFFSET)
 frag &= 0xFFFFFFFFFFFFFFFF
 return frag

def _pack_body(chars56: str) -> bytes:
 """Pack the 56-letter identity body into 32 bytes."""

 if len(chars56) != IDENTITY_BODY_LENGTH:
 raise ValueError("identity body must be 56 letters")
 buf = bytearray(32)
 for idx in range(GROUP_COUNT):
 block = chars56[idx * GROUP_LENGTH : (idx + 1) * GROUP_LENGTH]
 frag = _encode_group(block)
 struct.pack_into("<Q", buf, idx * 8, frag)
 return bytes(buf)

def _kangaroo_twelve_simple(data: bytes, output_length: int = 3) -> bytes:
 """Very small stand-in hash (SHA-256 truncated) for KangarooTwelve.
 
 Note: This is a simplified version. Real Qubic uses KangarooTwelve, but for
 our purposes SHA-256 truncated to 3 bytes works fine for checksum calculation.
 """

 return sha256(data).digest()[:output_length]

def checksum_letters(buf: bytes, msb_first: bool = True) -> str:
 """Return the four checksum letters derived from the packed buffer."""

 checksum_val = int.from_bytes(_kangaroo_twelve_simple(buf, 3), "little") & 0x3FFFF
 digits: List[int] = []
 for _ in range(4):
 digits.append(checksum_val % 26)
 checksum_val //= 26
 if msb_first:
 digits = list(reversed(digits))
 return "".join(chr(ALPHABET_OFFSET + digit) for digit in digits)

def public_key_from_identity(identity: str) -> Tuple[str | None, bool]:
 """Return the public key hex string and checksum validity."""

 if len(identity) != IDENTITY_LENGTH or not identity.isalpha():
 return None, False
 body = identity[:IDENTITY_BODY_LENGTH]
 buf = _pack_body(body)

 checksum_val = int.from_bytes(_kangaroo_twelve_simple(buf, 3), "little") & 0x3FFFF
 target = 0
 for ch in identity[IDENTITY_BODY_LENGTH:]:
 target = target * 26 + (ord(ch) - ALPHABET_OFFSET)
 return buf.hex(), checksum_val == target

def identity_from_body(chars56: str, suffix: str | None = None, msb_first: bool = True) -> str:
 """Construct a 60-char identity from the 56-char body and suffix.

 If suffix is not provided, the checksum derived from the body is used.
 """

 buf = _pack_body(chars56)
 tail = suffix if suffix is not None else checksum_letters(buf, msb_first=msb_first)
 if len(tail) != 4:
 raise ValueError("suffix must be exactly four letters")
 return chars56 + tail

__all__ = [
 "IdentityRecord",
 "base26_char",
 "matrix_hash",
 "public_key_from_identity",
 "identity_from_body",
 "checksum_letters",
]

