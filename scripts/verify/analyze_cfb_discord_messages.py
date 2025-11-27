#!/usr/bin/env python3
"""
Analyze CFB Discord Messages for Puzzle Clues

Searches for keywords, patterns, and extracts relevant information.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
MESSAGES_FILE = OUTPUT_DIR / "cfb_messages_channel_768890598736003092.json"
ANALYSIS_FILE = OUTPUT_DIR / "cfb_messages_analysis.json"
REPORT_FILE = OUTPUT_DIR / "cfb_messages_analysis.md"

def analyze_messages(messages: List[dict]) -> dict:
 """Analyze CFB messages for relevant patterns."""
 
 analysis = {
 "total_messages": len(messages),
 "date_range": {
 "earliest": None,
 "latest": None,
 },
 "keywords": {
 "matrix": [],
 "anna": [],
 "puzzle": [],
 "reward": [],
 "contract": [],
 "genesis": [],
 "26": [],
 "676": [],
 "128": [],
 "block": [],
 "layer": [],
 "seed": [],
 "identity": [],
 "public_key": [],
 "encoding": [],
 "decode": [],
 "hidden": [],
 "secret": [],
 },
 "relevant_messages": [],
 "word_frequency": {},
 }
 
 keywords_map = {
 "matrix": ["matrix", "anna-matrix"],
 "anna": ["anna", "@anna"],
 "puzzle": ["puzzle", "riddle", "challenge"],
 "reward": ["reward", "prize", "treasure"],
 "contract": ["contract", "smart contract"],
 "genesis": ["genesis", "asset", "token", "qcap"],
 "26": ["26", "twenty-six"],
 "676": ["676", "six hundred seventy-six"],
 "128": ["128", "one hundred twenty-eight"],
 "block": ["block", "block-id"],
 "layer": ["layer", "layer 2", "layer2"],
 "seed": ["seed"],
 "identity": ["identity", "public key", "publickey"],
 "public_key": ["public key", "publickey", "key"],
 "encoding": ["encoding", "encode", "encoded"],
 "decode": ["decode", "decoding", "decoded"],
 "hidden": ["hidden", "hide", "secret"],
 "secret": ["secret", "hidden"],
 }
 
 timestamps = []
 all_words = []
 
 for msg in messages:
 content = msg.get("content", "").lower()
 timestamp = msg.get("timestamp", "")
 message_id = msg.get("id", "")
 
 if timestamp:
 timestamps.append(timestamp)
 
 # Extract words
 words = content.split()
 all_words.extend(words)
 
 relevant = False
 
 # Check keywords
 for category, terms in keywords_map.items():
 for term in terms:
 if term.lower() in content:
 analysis["keywords"][category].append({
 "id": message_id,
 "timestamp": timestamp,
 "preview": content[:200],
 "full_content": msg.get("content", ""),
 })
 relevant = True
 
 if relevant:
 analysis["relevant_messages"].append({
 "id": message_id,
 "timestamp": timestamp,
 "content": msg.get("content", ""),
 })
 
 # Date range
 if timestamps:
 analysis["date_range"]["earliest"] = min(timestamps)
 analysis["date_range"]["latest"] = max(timestamps)
 
 # Word frequency
 word_counts = Counter(all_words)
 # Filter out common words
 common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "what", "which", "who", "where", "when", "why", "how"}
 filtered_words = {word: count for word, count in word_counts.items() if word not in common_words and len(word) > 3}
 # Convert back to Counter for most_common
 filtered_counter = Counter(filtered_words)
 analysis["word_frequency"] = dict(filtered_counter.most_common(50))
 
 return analysis

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("📊 CFB DISCORD MESSAGES ANALYSE")
 print("=" * 80)
 print()
 
 if not MESSAGES_FILE.exists():
 print(f"❌ Messages file not found: {MESSAGES_FILE}")
 return 1
 
 with MESSAGES_FILE.open(encoding="utf-8") as f:
 messages = json.load(f)
 
 print(f"📥 Loaded {len(messages)} CFB messages")
 print()
 
 # Analyze
 print("Analyzing messages...")
 analysis = analyze_messages(messages)
 
 # Save analysis
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with ANALYSIS_FILE.open("w", encoding="utf-8") as f:
 json.dump(analysis, f, indent=2, ensure_ascii=False)
 
 # Create markdown report
 with REPORT_FILE.open("w", encoding="utf-8") as f:
 f.write("# CFB Discord Messages Analysis\n\n")
 f.write(f"**Total Messages:** {analysis['total_messages']}\n\n")
 
 if analysis["date_range"]["earliest"]:
 f.write(f"**Date Range:** {analysis['date_range']['earliest'][:10]} to {analysis['date_range']['latest'][:10]}\n\n")
 
 f.write("## Keywords Found\n\n")
 for category, matches in analysis["keywords"].items():
 if matches:
 f.write(f"### {category.upper()} ({len(matches)} matches)\n\n")
 for match in matches[:5]:
 f.write(f"- **{match['timestamp'][:19]}**: {match['preview']}...\n")
 f.write("\n")
 
 f.write("## Relevant Messages\n\n")
 for msg in analysis["relevant_messages"][:20]:
 f.write(f"### {msg['timestamp'][:19]}\n\n")
 f.write(f"{msg['content']}\n\n")
 f.write("---\n\n")
 
 f.write("## Word Frequency (Top 20)\n\n")
 for word, count in list(analysis["word_frequency"].items())[:20]:
 f.write(f"- {word}: {count}\n")
 
 # Print summary
 print()
 print("=" * 80)
 print("✅ ANALYSE COMPLETE")
 print("=" * 80)
 print()
 print(f"Total messages: {analysis['total_messages']}")
 if analysis["date_range"]["earliest"]:
 print(f"Date range: {analysis['date_range']['earliest'][:10]} to {analysis['date_range']['latest'][:10]}")
 print()
 
 print("Keywords found:")
 for category, matches in analysis["keywords"].items():
 if matches:
 print(f" {category}: {len(matches)} matches")
 print()
 
 print(f"💾 Analysis saved to:")
 print(f" {ANALYSIS_FILE}")
 print(f" {REPORT_FILE}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

