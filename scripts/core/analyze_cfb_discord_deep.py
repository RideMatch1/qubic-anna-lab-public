#!/usr/bin/env python3
"""
Deep Dive in CFB Discord Messages - Suche nach spezifischen Hinweisen zu:
- Anna Matrix
- Aigarth
- Identities
- Helix Gates
- Evolution
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from collections import defaultdict, Counter
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

# Spezifische Keywords for Deep Dive
DEEP_KEYWORDS = {
 "anna_matrix": [
 "anna matrix", "anna-matrix", "anna_matrix",
 "matrix", "128x128", "excel",
 ],
 "aigarth": [
 "aigarth", "Aigarth", "AIGARTH",
 "intelligent tissue", "tissue",
 ],
 "helix": [
 "helix", "Helix", "helix gate", "Helix gate",
 "logic gate", "A+B+C", "rotation",
 ],
 "identity": [
 "identity", "identities", "public key",
 "seed", "60 char", "56 char",
 ],
 "evolution": [
 "evolution", "evolutionary", "selection",
 "fittest", "fitness", "self-modification",
 ],
 "layer": [
 "layer", "Layer", "layer-2", "Layer-2",
 "layer 2", "Layer 2", "layer2",
 ],
 "oracle": [
 "oracle", "Oracle", "oracle machine",
 "Oracle Machine", "oracle machines",
 ],
 "hint": [
 "hint", "Hint", "clue", "Clue",
 "26", "676", "base-26", "base26",
 ],
}

def load_cfb_messages() -> List[Dict]:
 """Load alle CFB Discord Messages."""
 
 messages = []
 cfb_dir = OUTPUT_DIR / "cfb_discord_messages"
 
 if not cfb_dir.exists():
 print(f"⚠️ CFB messages directory not found: {cfb_dir}")
 return messages
 
 # Load alle JSON-Dateien
 for json_file in cfb_dir.glob("*.json"):
 try:
 with json_file.open() as f:
 data = json.load(f)
 
 # Verschiedene JSON-Formate möglich
 if isinstance(data, list):
 messages.extend(data)
 elif isinstance(data, dict):
 if "messages" in data:
 messages.extend(data["messages"])
 elif "content" in data:
 messages.append(data)
 except Exception as e:
 print(f"⚠️ Error loading {json_file}: {e}")
 
 return messages

def search_keywords_in_message(message: Dict, keywords: Dict) -> Dict:
 """Suche Keywords in einer Message."""
 
 content = message.get("content", "").lower()
 author = message.get("author", {})
 author_id = author.get("id", "")
 timestamp = message.get("timestamp", "")
 
 matches = defaultdict(list)
 
 for category, keyword_list in keywords.items():
 for keyword in keyword_list:
 pattern = re.compile(re.escape(keyword.lower()), re.IGNORECASE)
 
 if pattern.search(content):
 # Extrahiere Context
 matches_in_content = list(pattern.finditer(content))
 for match in matches_in_content:
 start = max(0, match.start() - 100)
 end = min(len(content), match.end() + 100)
 context = content[start:end].replace('\n', ' ').strip()
 
 matches[category].append({
 "keyword": keyword,
 "context": context,
 "position": match.start(),
 })
 
 return dict(matches)

def analyze_cfb_messages(messages: List[Dict]) -> Dict:
 """Analyze CFB Messages for relevante Hinweise."""
 
 results = {
 "total_messages": len(messages),
 "keyword_matches": defaultdict(list),
 "relevant_messages": [],
 "keyword_statistics": {},
 }
 
 for msg in messages:
 matches = search_keywords_in_message(msg, DEEP_KEYWORDS)
 
 if matches:
 # Message ist relevant
 relevant_msg = {
 "id": msg.get("id", ""),
 "timestamp": msg.get("timestamp", ""),
 "content": msg.get("content", ""),
 "matches": matches,
 }
 
 results["relevant_messages"].append(relevant_msg)
 
 # Aggregiere Matches
 for category, match_list in matches.items():
 results["keyword_matches"][category].extend(match_list)
 
 # Statistik
 for category, match_list in results["keyword_matches"].items():
 results["keyword_statistics"][category] = len(match_list)
 
 return results

def extract_specific_hints(messages: List[Dict]) -> List[Dict]:
 """Extrahiere spezifische Hinweise von CFB."""
 
 hints = []
 
 hint_patterns = [
 r"26",
 r"676",
 r"base-?26",
 r"128",
 r"helix",
 r"evolution",
 r"identity",
 r"layer",
 r"oracle",
 ]
 
 for msg in messages:
 content = msg.get("content", "").lower()
 
 for pattern in hint_patterns:
 if re.search(pattern, content, re.IGNORECASE):
 hints.append({
 "id": msg.get("id", ""),
 "timestamp": msg.get("timestamp", ""),
 "content": msg.get("content", ""),
 "pattern": pattern,
 })
 break # Nur einmal pro Message
 
 return hints

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("CFB DISCORD MESSAGES DEEP DIVE")
 print("=" * 80)
 print()
 
 print("Loading CFB messages...")
 messages = load_cfb_messages()
 print(f"✅ Loaded {len(messages)} messages")
 print()
 
 if not messages:
 print("⚠️ No messages found. Check if CFB messages are exported.")
 return
 
 print("Analyzing messages for keywords...")
 analysis = analyze_cfb_messages(messages)
 print(f"✅ Found {len(analysis['relevant_messages'])} relevant messages")
 print()
 
 print("Extracting specific hints...")
 hints = extract_specific_hints(messages)
 print(f"✅ Found {len(hints)} potential hints")
 print()
 
 # Zeige Statistik
 print("=" * 80)
 print("KEYWORD STATISTICS")
 print("=" * 80)
 print()
 
 for category, count in sorted(analysis["keyword_statistics"].items(), key=lambda x: x[1], reverse=True):
 print(f"{category.upper()}: {count} matches")
 print()
 
 # Zeige Top 10 relevante Messages
 print("=" * 80)
 print("TOP 10 RELEVANT MESSAGES")
 print("=" * 80)
 print()
 
 # Sortiere nach Anzahl Matches
 sorted_messages = sorted(
 analysis["relevant_messages"],
 key=lambda x: sum(len(m) for m in x["matches"].values()),
 reverse=True
 )
 
 for i, msg in enumerate(sorted_messages[:10], 1):
 print(f"{i}. Message ID: {msg['id']}")
 print(f" Timestamp: {msg['timestamp']}")
 print(f" Matches: {sum(len(m) for m in msg['matches'].values())} keywords")
 print(f" Preview: {msg['content'][:200]}...")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "cfb_discord_deep_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "analysis": analysis,
 "hints": hints,
 "timestamp": datetime.now().isoformat(),
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "cfb_discord_deep_analysis_report.md"
 
 with report_file.open("w") as f:
 f.write("# CFB Discord Messages Deep Dive Report\n\n")
 f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
 f.write("## Overview\n\n")
 f.write(f"- **Total messages analyzed**: {analysis['total_messages']}\n")
 f.write(f"- **Relevant messages found**: {len(analysis['relevant_messages'])}\n")
 f.write(f"- **Potential hints extracted**: {len(hints)}\n\n")
 
 f.write("## Keyword Statistics\n\n")
 for category, count in sorted(analysis["keyword_statistics"].items(), key=lambda x: x[1], reverse=True):
 f.write(f"- **{category}**: {count} matches\n")
 f.write("\n")
 
 f.write("## Top Relevant Messages\n\n")
 for i, msg in enumerate(sorted_messages[:20], 1):
 f.write(f"### Message {i}\n\n")
 f.write(f"- **ID**: {msg['id']}\n")
 f.write(f"- **Timestamp**: {msg['timestamp']}\n")
 f.write(f"- **Matches**: {sum(len(m) for m in msg['matches'].values())} keywords\n")
 f.write(f"- **Content**:\n\n")
 f.write(f"```\n{msg['content']}\n```\n\n")
 
 f.write("## Potential Hints\n\n")
 for i, hint in enumerate(hints[:20], 1):
 f.write(f"{i}. **Pattern**: {hint['pattern']}\n")
 f.write(f" **Timestamp**: {hint['timestamp']}\n")
 f.write(f" **Content**: {hint['content'][:300]}...\n\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ CFB DISCORD DEEP DIVE COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

