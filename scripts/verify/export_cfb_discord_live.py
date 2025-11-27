#!/usr/bin/env python3
"""
Live CFB Discord Message Exporter with Real-time Output

Exports only CFB's messages with live progress display.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092"
GUILD_ID = "768887649540243497"

# Paths
EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

def export_channel_json(
 token: str,
 channel_id: str,
 output_file: Path,
 after: Optional[str] = None,
) -> bool:
 """Export channel to JSON with live output."""
 if not EXPORTER_PATH.exists():
 print(f"❌ DiscordChatExporter.Cli not found at: {EXPORTER_PATH}")
 return False
 
 cmd = [
 str(EXPORTER_PATH),
 "export",
 "--channel", channel_id,
 "--token", token,
 "--output", str(output_file),
 "--format", "Json",
 "--markdown", "True",
 ]
 
 if after:
 cmd.extend(["--after", after])
 
 try:
 # Run with live output
 process = subprocess.Popen(
 cmd,
 stdout=subprocess.PIPE,
 stderr=subprocess.STDOUT,
 text=True,
 bufsize=1,
 universal_newlines=True,
 )
 
 # Print output live
 for line in process.stdout:
 print(line, end='', flush=True)
 
 process.wait()
 return process.returncode == 0
 except Exception as e:
 print(f"❌ Error: {e}")
 return False

def filter_cfb_messages(json_file: Path) -> list:
 """Filter messages from CFB's user ID."""
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 if "messages" in data:
 for msg in data["messages"]:
 author = msg.get("author", {})
 if author.get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 except Exception as e:
 print(f"❌ Error filtering: {e}")
 return []

def load_existing_messages() -> list:
 """Load already exported messages."""
 if MESSAGES_FILE.exists():
 try:
 with MESSAGES_FILE.open(encoding="utf-8") as f:
 return json.load(f)
 except Exception:
 pass
 return []

def save_messages(messages: list):
 """Save messages."""
 with MESSAGES_FILE.open("w", encoding="utf-8") as f:
 json.dump(messages, f, indent=2, ensure_ascii=False)

def main() -> int:
 """Main export function with live output."""
 
 print("=" * 80)
 print("🚀 LIVE CFB DISCORD MESSAGE EXPORTER")
 print("=" * 80)
 print()
 
 # Get token
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN environment variable not set!")
 return 1
 
 print(f"✅ Token found (length: {len(token)})")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB User ID: {CFB_USER_ID}")
 print()
 
 # Load existing messages
 all_messages = load_existing_messages()
 if all_messages:
 print(f"📥 Resuming: Already have {len(all_messages)} messages")
 print()
 
 batch_num = 0
 last_message_id = None
 
 # Get last message ID from existing messages
 if all_messages:
 last_message_id = all_messages[-1].get("id")
 print(f"📌 Resuming from message ID: {last_message_id}")
 print()
 
 print("Starting export (Ctrl+C to stop, progress will be saved)...")
 print()
 
 try:
 while True:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}_temp.json"
 
 print(f"📦 Batch {batch_num} | ", end="", flush=True)
 
 # Export batch
 print("Exporting... ", end="", flush=True)
 success = export_channel_json(
 token=token,
 channel_id=CHANNEL_ID,
 output_file=temp_file,
 after=last_message_id,
 )
 
 if not success:
 print("❌ Failed")
 break
 
 print("✅ | ", end="", flush=True)
 
 # Filter CFB messages
 print("Filtering... ", end="", flush=True)
 batch_cfb = filter_cfb_messages(temp_file)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 print(f"0 CFB messages")
 
 # Check if channel is exhausted
 try:
 with temp_file.open(encoding="utf-8") as f:
 data = json.load(f)
 if not data.get("messages"):
 print(" ✅ No more messages in channel")
 temp_file.unlink(missing_ok=True)
 break
 except Exception:
 pass
 else:
 print(f"{batch_size} CFB messages found! ✅")
 all_messages.extend(batch_cfb)
 
 # Update last message ID
 if batch_cfb:
 last_message_id = batch_cfb[-1].get("id")
 
 # Save incrementally
 save_messages(all_messages)
 print(f" 💾 Saved: {len(all_messages)} total CFB messages")
 print()
 
 # Cleanup temp file
 temp_file.unlink(missing_ok=True)
 
 # Stop if no CFB messages in batch
 if batch_size == 0:
 print(" ⏸️ No CFB messages in this batch, stopping")
 break
 
 # Small delay
 time.sleep(0.5)
 
 except KeyboardInterrupt:
 print()
 print()
 print("⚠️ Interrupted by user")
 print(f"✅ Progress saved: {len(all_messages)} messages from {batch_num} batches")
 save_messages(all_messages)
 return 0
 
 except Exception as e:
 print()
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()
 save_messages(all_messages)
 return 1
 
 # Final save
 save_messages(all_messages)
 
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 print()
 print(f"Total batches: {batch_num}")
 print(f"Total CFB messages: {len(all_messages)}")
 print(f"Saved to: {MESSAGES_FILE}")
 print()
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

