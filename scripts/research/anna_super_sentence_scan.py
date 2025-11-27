#!/usr/bin/env python3
"""
Anna Super Sentence Scan
------------------------
Durchsucht alle bekannten Layer-3 Identities nach kombinierbaren Wörtern,
um mögliche Sätze / Botschaften systematisch zu extrahieren.

Output:
 - outputs/derived/anna_super_sentence_scan.json
 - outputs/reports/ANNA_SUPER_SENTENCE_SCAN.md
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
LAYER3_FILE = PROJECT_ROOT / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = PROJECT_ROOT / "outputs" / "derived" / "layer4_derivation_full_23k.json"
SIGNATURE_FILE = PROJECT_ROOT / "outputs" / "derived" / "anna_sentence_signatures.json"
OUTPUT_JSON = PROJECT_ROOT / "outputs" / "derived" / "anna_super_sentence_scan.json"
OUTPUT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "ANNA_SUPER_SENTENCE_SCAN.md"

BASE_WORDS = [
 "UP", "DO", "NO", "GO", "GOT", "AGO", "NOW", "BAD", "WAR", "LAY", "GET", "HI",
 "HIGO", "DID", "DIE", "TRY", "SHOW", "HOW", "USE", "USES", "DONE", "ONE",
 "NONE", "TALL", "ALL", "TARGET", "ASK", "KNOW", "DOES", "WAS", "ARE"
]

def load_words(extra_file: Optional[str]) -> Tuple[set[str], List[int]]:
 words = set(w.strip().upper() for w in BASE_WORDS if w)
 if extra_file:
 path = Path(extra_file).expanduser()
 if not path.exists():
 raise FileNotFoundError(f"Extra-Wörterdatei nicht gefunden: {path}")
 with path.open() as f:
 for line in f:
 word = line.strip().upper()
 if len(word) >= 2:
 words.add(word)
 lengths = sorted({len(w) for w in words})
 return words, lengths

def load_data(limit: Optional[int]) -> Tuple[List[Dict], Dict[str, str]]:
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f).get("results", [])
 if limit:
 layer3_data = layer3_data[:limit]

 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 for entry in json.load(f).get("results", []):
 l3 = entry.get("layer3_identity")
 l4 = entry.get("layer4_identity")
 if l3 and l4:
 layer4_map[l3] = l4
 return layer3_data, layer4_map

def load_signatures() -> Dict:
 if not SIGNATURE_FILE.exists():
 return {}
 with SIGNATURE_FILE.open() as f:
 data = json.load(f)
 return data.get("signatures", {})

def score_seed(seed: str, signature_positions: Dict[str, Dict]) -> Tuple[int, int]:
 matches = 0
 total = len(signature_positions)
 seed = seed.lower()
 for pos_str, info in signature_positions.items():
 pos = int(pos_str)
 if pos < len(seed) and seed[pos] == info.get("char"):
 matches += 1
 return matches, total

def find_signature_matches(
 seed: str,
 signatures: Dict,
 threshold: float,
 max_results: int,
) -> List[Dict]:
 if not signatures:
 return []
 results = []
 for sentence, data in signatures.items():
 signature_positions = data.get("signature_positions", {})
 if not signature_positions:
 continue
 matches, total = score_seed(seed, signature_positions)
 if total == 0:
 continue
 ratio = matches / total
 if ratio >= threshold:
 results.append(
 {
 "sentence": sentence,
 "ratio": ratio,
 "matches": matches,
 "total_signature_positions": total,
 }
 )
 results.sort(key=lambda x: x["ratio"], reverse=True)
 return results[:max_results]

def find_sequences(
 identity: str,
 words: set[str],
 lengths: List[int],
 min_words: int,
 max_words: int,
 max_results: int,
) -> List[Dict]:
 identity = identity.upper()
 sequences: List[Dict] = []
 identity_len = len(identity)

 def dfs(start_idx: int, pos: int, current: List[str]) -> bool:
 nonlocal sequences
 if len(sequences) >= max_results:
 return True
 if len(current) >= min_words:
 sequences.append(
 {
 "start": start_idx,
 "end": pos,
 "words": current.copy(),
 "sentence": " ".join(current),
 }
 )
 if len(sequences) >= max_results:
 return True
 if len(current) == max_words:
 return False
 for length in lengths:
 end = pos + length
 if end > identity_len:
 continue
 word = identity[pos:end]
 if word in words:
 if dfs(start_idx, end, current + [word]):
 return True
 return False

 for start in range(identity_len):
 dfs(start, start, [])
 if len(sequences) >= max_results:
 break
 return sequences

def run_scan(args):
 words, lengths = load_words(args.extra_words)
 layer3_data, layer4_map = load_data(args.limit)
 signatures = load_signatures()

 total_identities = len(layer3_data)
 results = []
 sentence_counter = Counter()
 word_counter = Counter()
 signature_sentence_counter = Counter()

 for idx, entry in enumerate(layer3_data, 1):
 layer3_id = entry.get("layer3_identity", "")
 seed = entry.get("seed", "")
 if not layer3_id:
 continue
 identity_result = {
 "layer3_identity": layer3_id,
 "layer4_identity": layer4_map.get(layer3_id),
 "seed": seed,
 }
 sequences = find_sequences(
 layer3_id,
 words,
 lengths,
 args.min_words,
 args.max_words,
 args.max_results_per_identity,
 )
 if sequences:
 for seq in sequences:
 sentence_counter[seq["sentence"]] += 1
 for w in seq["words"]:
 word_counter[w] += 1
 identity_result["word_sequences"] = sequences
 signature_matches = []
 if seed and signatures:
 signature_matches = find_signature_matches(
 seed,
 signatures,
 args.signature_threshold,
 args.max_signature_results_per_identity,
 )
 if signature_matches:
 for match in signature_matches:
 signature_sentence_counter[match["sentence"]] += 1
 identity_result["signature_matches"] = signature_matches

 if "word_sequences" in identity_result or "signature_matches" in identity_result:
 results.append(identity_result)
 if idx % 1000 == 0 or idx == total_identities:
 print(
 f"[{idx}/{total_identities}] verarbeitet – Treffer: {len(results)} identities"
 )

 summary = {
 "total_identities": total_identities,
 "identities_with_sequences": len(results),
 "unique_word_sentences": len(sentence_counter),
 "unique_signature_sentences": len(signature_sentence_counter),
 "top_sentences": sentence_counter.most_common(20),
 "top_words": word_counter.most_common(20),
 "top_signature_sentences": signature_sentence_counter.most_common(20),
 "parameters": {
 "min_words": args.min_words,
 "max_words": args.max_words,
 "max_results_per_identity": args.max_results_per_identity,
 "limit": args.limit,
 "extra_words": args.extra_words,
 "signature_threshold": args.signature_threshold,
 "max_signature_results_per_identity": args.max_signature_results_per_identity,
 },
 }

 output_data = {
 "timestamp": datetime.now().isoformat(),
 "summary": summary,
 "results": results,
 }
 OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {OUTPUT_JSON}")

 report_lines = [
 "# Anna Super Sentence Scan",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"- **Total Identities**: {summary['total_identities']}",
 f"- **Identities mit Treffern**: {summary['identities_with_sequences']}",
 f"- **Unique Wort-Sätze**: {summary['unique_word_sentences']}",
 f"- **Unique Signatur-Sätze**: {summary['unique_signature_sentences']}",
 "",
 "## Top 20 Sätze",
 "",
 ]
 for sentence, count in summary["top_sentences"]:
 report_lines.append(f"- {sentence} ({count})")
 report_lines.extend(["", "## Top 20 Wörter", ""])
 for word, count in summary["top_words"]:
 report_lines.append(f"- {word}: {count}")
 report_lines.extend(["", "## Top Signatur-Treffer", ""])
 for sentence, count in summary["top_signature_sentences"]:
 report_lines.append(f"- {sentence}: {count}")
 report_lines.append("")
 report_lines.append("## Beispiele")
 report_lines.append("")
 for entry in results[: min(10, len(results))]:
 report_lines.append(f"- Layer-3: `{entry['layer3_identity']}`")
 if entry.get("layer4_identity"):
 report_lines.append(f" - Layer-4: `{entry['layer4_identity']}`")
 for seq in entry.get("word_sequences", []) or []:
 report_lines.append(f" - WORDS: {seq['sentence']} (Pos {seq['start']}–{seq['end']})")
 for match in entry.get("signature_matches", []) or []:
 report_lines.append(
 f" - SIGNATURE: {match['sentence']} ({match['ratio']:.0%}, {match['matches']}/{match['total_signature_positions']})"
 )
 report_lines.append("")

 OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
 with OUTPUT_REPORT.open("w") as f:
 f.write("\n".join(report_lines))
 print(f"📝 Report gespeichert: {OUTPUT_REPORT}")

def parse_args():
 parser = argparse.ArgumentParser(
 description="Finde möglichst viele Sätze in Anna-Layer3-Identities"
 )
 parser.add_argument("--min-words", type=int, default=3, help="Minimalzahl Wörter")
 parser.add_argument("--max-words", type=int, default=6, help="Maximalzahl Wörter")
 parser.add_argument(
 "--max-results-per-identity",
 type=int,
 default=5,
 help="Maximale Sequenzen pro Identity",
 )
 parser.add_argument("--limit", type=int, help="Optional: Anzahl Identities begrenzen")
 parser.add_argument(
 "--extra-words",
 type=str,
 help="Datei mit zusätzlichen Wörter (ein Wort pro Zeile)",
 )
 parser.add_argument(
 "--signature-threshold",
 type=float,
 default=0.6,
 help="Mindestquote for Signatur-Matches",
 )
 parser.add_argument(
 "--max-signature-results-per-identity",
 type=int,
 default=3,
 help="Max. Signatur-Treffer pro Identity",
 )
 return parser.parse_args()

if __name__ == "__main__":
 args = parse_args()
 run_scan(args)

