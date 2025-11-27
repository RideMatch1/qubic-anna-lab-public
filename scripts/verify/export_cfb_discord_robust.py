#!/usr/bin/env python3
"""
Robust CFB Discord Message Exporter with Live Output

Exports only CFB's messages with real-time progress display.
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
) -> tuple[bool, str]:
 """Export channel to JSON with live output. Returns (success, error_message)."""
 if not EXPORTER_PATH.exists():
 return False, f"DiscordChatExporter.Cli not found at: {EXPORTER_PATH}"
 
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
 print(" [Export läuft...] ", end="", flush=True)
 
 # Run with timeout and capture output
 result = subprocess.run(
 cmd,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True,
 timeout=180, # 3 minutes max
 )
 
 if result.returncode == 0:
 print("✅", flush=True)
 return True, ""
 else:
 error = result.stderr[:200] if result.stderr else "Unknown error"
 print(f"❌ ({error})", flush=True)
 return False, error
 
 except subprocess.TimeoutExpired:
 print("⏱️ Timeout", flush=True)
 return False, "Timeout after 3 minutes"
 except Exception as e:
 print(f"❌ Error: {e}", flush=True)
 return False, str(e)

def filter_cfb_messages(json_file: Path) -> list:
 """Filter messages from CFB's user ID."""
 if not json_file.exists():
 return []
 
 try:
 # Check file size first
 if json_file.stat().st_size == 0:
 return []
 
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 if "messages" in data:
 for msg in data["messages"]:
 author = msg.get("author", {})
 if author.get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 except json.JSONDecodeError as e:
 print(f" ⚠️ JSON Error: {e}")
 return []
 except Exception as e:
 print(f" ⚠️ Error filtering: {e}")
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
 print("🚀 ROBUST CFB DISCORD MESSAGE EXPORTER")
 print("=" * 80)
 print()
 
 # Get token
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN environment variable not set!")
 return 1
 
 print(f"✅ Token: {token[:20]}...")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB User ID: {CFB_USER_ID}")
 print()
 
 # Load existing messages
 all_messages = load_existing_messages()
 if all_messages:
 print(f"📥 Resuming: Already have {len(all_messages)} messages")
 last_message_id = all_messages[-1].get("id")
 print(f"📌 Resuming from: {last_message_id}")
 else:
 last_message_id = None
 print("📥 Starting new export...")
 
 print()
 print("Starting export (Ctrl+C to stop, progress will be saved)...")
 print()
 
 batch_num = 0
 consecutive_empty = 0
 
 try:
 while True:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}_temp.json"
 
 print(f"Batch {batch_num:3d} | ", end="", flush=True)
 
 # Export batch
 success, error = export_channel_json(
 token=token,
 channel_id=CHANNEL_ID,
 output_file=temp_file,
 after=last_message_id,
 )
 
 if not success:
 print(f" ⚠️ Export failed: {error}")
 if "timeout" in error.lower():
 print(" Retrying in 2 seconds...")
 time.sleep(2)
 continue
 break
 
 # Filter CFB messages
 print(" [Filtering...] ", end="", flush=True)
 batch_cfb = filter_cfb_messages(temp_file)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 consecutive_empty += 1
 print(f"0 CFB | Total: {len(all_messages)}")
 
 # Check if channel is exhausted
 try:
 if temp_file.exists() and temp_file.stat().st_size > 0:
 with temp_file.open(encoding="utf-8") as f:
 data = json.load(f)
 if not data.get("messages"):
 print(" ✅ No more messages in channel")
 temp_file.unlink(missing_ok=True)
 break
 except Exception:
 pass
 
 if consecutive_empty >= 3:
 print(" ⏸️ No CFB messages in last 3 batches, stopping")
 break
 else:
 consecutive_empty = 0
 all_messages.extend(batch_cfb)
 print(f"{batch_size:3d} CFB ✅ | Total: {len(all_messages)}")
 
 # Update last message ID
 if batch_cfb:
 last_message_id = batch_cfb[-1].get("id")
 
 # Save incrementally
 save_messages(all_messages)
 
 # Cleanup temp file
 temp_file.unlink(missing_ok=True)
 
 # Small delay
 time.sleep(0.3)
 
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

