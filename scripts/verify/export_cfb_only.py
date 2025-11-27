#!/usr/bin/env python3
"""
Export ONLY CFB Messages - Efficient filtering during export

Uses DiscordChatExporter with --filter to only get CFB's messages.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092"

# Paths
EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

def export_cfb_only(token: str, channel_id: str, output_file: Path) -> bool:
 """Export ONLY CFB messages using filter."""
 if not EXPORTER_PATH.exists():
 print(f"❌ DiscordChatExporter.Cli not found")
 return False
 
 # DiscordChatExporter filter syntax: "from:USER_ID"
 filter_expr = f"from:{CFB_USER_ID}"
 
 cmd = [
 str(EXPORTER_PATH),
 "export",
 "--channel", channel_id,
 "--token", token,
 "--output", str(output_file),
 "--format", "Json",
 "--filter", filter_expr,
 "--markdown", "True",
 ]
 
 print("🚀 Exporting ONLY CFB messages...")
 print(f" Filter: {filter_expr}")
 print()
 
 try:
 process = subprocess.Popen(
 cmd,
 stdout=subprocess.PIPE,
 stderr=subprocess.STDOUT,
 text=True,
 bufsize=1,
 )
 
 # Show live output
 for line in process.stdout:
 print(line, end='', flush=True)
 
 process.wait()
 return process.returncode == 0
 
 except Exception as e:
 print(f"❌ Error: {e}")
 return False

def extract_cfb_messages(json_file: Path) -> list:
 """Extract CFB messages from export."""
 if not json_file.exists():
 return []
 
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 # If filter worked, all messages should be CFB's
 messages = data.get("messages", [])
 
 # Double-check filter
 cfb_messages = []
 for msg in messages:
 if msg.get("author", {}).get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 
 except Exception as e:
 print(f"❌ Error reading export: {e}")
 return []

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("🚀 EXPORT NUR CFB-NACHRICHTEN")
 print("=" * 80)
 print()
 
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN not set!")
 return 1
 
 print(f"✅ Token: {token[:20]}...")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB ID: {CFB_USER_ID}")
 print()
 
 temp_file = OUTPUT_DIR / "cfb_export_temp.json"
 
 # Export with filter
 success = export_cfb_only(token, CHANNEL_ID, temp_file)
 
 if not success:
 print("\n❌ Export failed!")
 return 1
 
 print()
 print("📥 Extracting CFB messages...")
 
 # Extract messages
 cfb_messages = extract_cfb_messages(temp_file)
 
 if not cfb_messages:
 print("❌ No CFB messages found!")
 return 1
 
 # Remove duplicates
 seen = set()
 unique = []
 for msg in cfb_messages:
 msg_id = msg.get("id")
 if msg_id and msg_id not in seen:
 seen.add(msg_id)
 unique.append(msg)
 
 # Save
 with MESSAGES_FILE.open("w", encoding="utf-8") as f:
 json.dump(unique, f, indent=2, ensure_ascii=False)
 
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 print()
 print(f"📊 Total CFB messages: {len(unique)}")
 print(f"💾 Saved to: {MESSAGES_FILE}")
 print()
 
 if unique:
 print("Erste 3 Nachrichten:")
 for i, msg in enumerate(unique[:3], 1):
 timestamp = msg.get("timestamp", "N/A")
 content = msg.get("content", "")[:100]
 print(f" {i}. [{timestamp}] {content}...")
 
 # Cleanup
 temp_file.unlink(missing_ok=True)
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

