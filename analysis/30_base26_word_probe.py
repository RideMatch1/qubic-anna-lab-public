#!/usr/bin/env python3
"""
Scan the full Base-26 stream for meaningful words, palindromes, and repeating motifs.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from analysis.utils.data_loader import ensure_directory, load_anna_matrix
from analysis.utils.identity_tools import base26_char, matrix_hash

TARGET_WORDS: Tuple[str, ...] = (
 "CFB",
 "COME",
 "BEYOND",
 "BASE",
 "QU",
 "QUBIC",
 "ANNA",
 "MATRIX",
 "VORTEX",
 "ROOT",
 "PUBLIC",
 "KEY",
 "KEYS",
 "DIGITAL",
 "SHIFT",
 "PROOF",
 "TWENTYSIX",
 "TWOSIX",
 "RUN",
 "TRINARY",
 "ANALOG",
 "BINARY",
)

OUTPUT_PATH = Path("outputs/reports/base26_word_probe.md")

def matrix_to_stream(matrix) -> str:
 """Flatten the matrix into a single Base-26 string."""

 letters = (base26_char(value) for value in matrix.flat)
 return "".join(letters)

def find_occurrences(stream: str, word: str) -> List[int]:
 """Return all start indices for the given word."""

 positions: List[int] = []
 start = 0
 while True:
 idx = stream.find(word, start)
 if idx == -1:
 break
 positions.append(idx)
 start = idx + 1
 return positions

def scan_dictionary(stream: str, words: Iterable[str]) -> List[Dict]:
 """Search the stream for the target dictionary words."""

 results: List[Dict] = []
 upper = stream.upper()
 for word in words:
 positions = find_occurrences(upper, word.upper())
 if positions:
 results.append(
 {
 "word": word,
 "count": len(positions),
 "positions": positions[:10],
 }
 )
 return results

def ngram_statistics(stream: str, length: int) -> List[Tuple[str, int]]:
 """Return the most common n-grams of the requested length."""

 counts = Counter(stream[i : i + length] for i in range(len(stream) - length + 1))
 return counts.most_common(10)

def palindrome_hits(stream: str, min_len: int = 6) -> List[str]:
 """Return palindromic substrings (limited set to avoid explosion)."""

 matches: List[str] = []
 seen: set[str] = set()
 n = len(stream)
 for length in range(min_len, min_len + 6):
 for start in range(0, n - length + 1):
 segment = stream[start : start + length]
 if segment == segment[::-1] and segment not in seen:
 seen.add(segment)
 matches.append(segment)
 if len(matches) >= 20:
 return matches
 return matches

def summarize_segments(stream: str, indices: Iterable[int], window: int = 30) -> Dict[int, str]:
 """Capture windows around interesting positions."""

 summaries: Dict[int, str] = {}
 n = len(stream)
 for idx in indices:
 start = max(idx - window, 0)
 end = min(idx + window, n)
 summaries[idx] = stream[start:end]
 return summaries

def main() -> None:
 payload = load_anna_matrix()
 matrix = payload.matrix
 stream = matrix_to_stream(matrix)

 reports_dir = ensure_directory(OUTPUT_PATH.parent)

 dictionary_hits = scan_dictionary(stream, TARGET_WORDS)
 tri_freq = ngram_statistics(stream, 3)
 quad_freq = ngram_statistics(stream, 4)
 palindromes = palindrome_hits(stream)

 # Collect all interesting indices for context windows.
 context_indices = []
 for entry in dictionary_hits:
 context_indices.extend(entry["positions"])
 context_snippets = summarize_segments(stream, context_indices)

 matrix_digest = matrix_hash(matrix)
 total_length = len(stream)

 lines: List[str] = []
 lines.append("# Base-26 Word Probe")
 lines.append("")
 lines.append(f"- Matrix source: `{payload.source_path}`")
 lines.append(f"- Matrix hash: `{matrix_digest}`")
 lines.append(f"- Base-26 stream length: {total_length}")
 lines.append("")
 lines.append("## Dictionary Hits")
 if dictionary_hits:
 for entry in dictionary_hits:
 lines.append(
 f"- `{entry['word']}` → {entry['count']} matches (first positions: {entry['positions']})"
 )
 else:
 lines.append("- No dictionary words found.")
 lines.append("")
 lines.append("## N-gram Top Frequencies")
 lines.append("### Trigrams")
 for gram, count in tri_freq:
 lines.append(f"- `{gram}` → {count}")
 lines.append("")
 lines.append("### Tetragrams")
 for gram, count in quad_freq:
 lines.append(f"- `{gram}` → {count}")
 lines.append("")
 lines.append("## Palindrome Candidates")
 if palindromes:
 for pal in palindromes:
 lines.append(f"- `{pal}`")
 else:
 lines.append("- None detected in scanned ranges.")
 lines.append("")
 lines.append("## Context Windows")
 if context_snippets:
 for idx, snippet in context_snippets.items():
 lines.append(f"- Pos {idx}: `{snippet}`")
 else:
 lines.append("- No snippets recorded.")

 OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

 print("[base26-word-probe] ✓ report ->", OUTPUT_PATH.resolve())

if __name__ == "__main__":
 main()

