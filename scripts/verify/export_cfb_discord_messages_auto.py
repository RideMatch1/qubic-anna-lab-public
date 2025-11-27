#!/usr/bin/env python3
"""
Export CFB Discord Messages - Auto Version

This version tries to find credentials automatically or uses command-line arguments.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")

def main():
 """Export CFB messages with credentials from command line or environment."""
 
 # Get credentials from command line args or environment
 if len(sys.argv) >= 3:
 token = sys.argv[1]
 channel_id = sys.argv[2]
 else:
 import os
 token = os.getenv("DISCORD_TOKEN")
 channel_id = os.getenv("DISCORD_CHANNEL_ID")
 
 if not token or not channel_id:
 print("Usage: python export_cfb_discord_messages_auto.py <token> <channel_id>")
 print(" or: export DISCORD_TOKEN=... DISCORD_CHANNEL_ID=... python export_cfb_discord_messages_auto.py")
 return 1
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "aigarth_channel.json"
 
 print(f"Exporting aigarth channel {channel_id}...")
 print(f"Output: {output_file}")
 print()
 
 cmd = [
 str(EXPORTER_PATH),
 "export",
 "--channel", channel_id,
 "--token", token,
 "--output", str(output_file),
 "--format", "Json",
 "--markdown", "True",
 ]
 
 try:
 result = subprocess.run(cmd, capture_output=True, text=True, check=True)
 print("✅ Export successful!")
 print(f" File: {output_file}")
 print()
 print("Now filtering CFB messages...")
 
 # Filter CFB messages
 with output_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 if "messages" in data:
 for msg in data["messages"]:
 author = msg.get("author", {})
 name = author.get("name", "").lower()
 if any(kw in name for kw in ["come-from-beyond", "cfb", "vfb", "sergey"]):
 cfb_messages.append(msg)
 
 print(f"✅ Found {len(cfb_messages)} messages from CFB")
 
 # Save filtered
 filtered_file = OUTPUT_DIR / "cfb_messages_filtered.json"
 with filtered_file.open("w", encoding="utf-8") as f:
 json.dump(cfb_messages, f, indent=2, ensure_ascii=False)
 
 print(f"✅ Saved to: {filtered_file}")
 return 0
 
 except subprocess.CalledProcessError as e:
 print(f"❌ Error: {e.stderr}")
 return 1
 except Exception as e:
 print(f"❌ Error: {e}")
 return 1

if __name__ == "__main__":
 raise SystemExit(main())

