#!/usr/bin/env python3
"""
Reverse-Chronological CFB Export - Startet mit neuesten Nachrichten

Geht rückwärts durch die Zeit und stoppt früh wenn keine CFB-Nachrichten mehr kommen.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092"
BATCH_SIZE = 100

# Paths
EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

def export_batch_reverse(token: str, channel_id: str, output_file: Path, after: str = None) -> tuple[bool, list]:
 """
 Export batch and return (success, messages).
 Goes backwards in time using --after parameter.
 """
 if not EXPORTER_PATH.exists():
 return False, []
 
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
 result = subprocess.run(
 cmd,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True,
 timeout=90, # 90 seconds max
 )
 
 if result.returncode != 0:
 error = result.stderr[:200] if result.stderr else "Unknown error"
 return False, []
 
 # Read and parse
 try:
 with output_file.open(encoding="utf-8") as f:
 data = json.load(f)
 messages = data.get("messages", [])
 return True, messages
 except Exception as e:
 return False, []
 
 except subprocess.TimeoutExpired:
 return False, []
 except Exception:
 return False, []

def filter_cfb(messages: list) -> list:
 """Filter only CFB messages."""
 return [m for m in messages if m.get("author", {}).get("id") == CFB_USER_ID]

def load_existing() -> tuple[list, str]:
 """Load existing messages."""
 if MESSAGES_FILE.exists():
 try:
 with MESSAGES_FILE.open(encoding="utf-8") as f:
 messages = json.load(f)
 last_id = messages[-1].get("id") if messages else None
 return messages, last_id
 except Exception:
 pass
 return [], None

def save_messages(messages: list):
 """Save messages, removing duplicates."""
 seen = set()
 unique = []
 for msg in messages:
 msg_id = msg.get("id")
 if msg_id and msg_id not in seen:
 seen.add(msg_id)
 unique.append(msg)
 
 with MESSAGES_FILE.open("w", encoding="utf-8") as f:
 json.dump(unique, f, indent=2, ensure_ascii=False)
 
 return unique

def main() -> int:
 """Main function - reverse chronological export."""
 print("=" * 80)
 print("🚀 REVERSE-CHRONOLOGICAL CFB EXPORT")
 print("=" * 80)
 print()
 
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN not set!")
 return 1
 
 print(f"✅ Token: {token[:20]}...")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB ID: {CFB_USER_ID}")
 print(f"📦 Strategy: Start with newest, go backwards")
 print()
 
 # Load existing
 all_cfb, last_id = load_existing()
 if all_cfb:
 print(f"📥 Resuming: {len(all_cfb)} CFB messages already saved")
 print(f"📌 Last message ID: {last_id}")
 else:
 print("📥 Starting from newest messages...")
 
 print()
 print("Starting export (Ctrl+C to stop, progress saved immediately)...")
 print()
 
 batch_num = 0
 consecutive_empty = 0
 max_empty = 10 # Stop after 10 empty batches
 
 try:
 while consecutive_empty < max_empty:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}.json"
 
 print(f"Batch {batch_num:3d} | ", end="", flush=True)
 
 # Export batch (going backwards)
 start_time = time.time()
 success, messages = export_batch_reverse(token, CHANNEL_ID, temp_file, after=last_id)
 elapsed = time.time() - start_time
 
 if not success:
 print(f"❌ Failed ({elapsed:.1f}s)")
 consecutive_empty += 1
 if consecutive_empty >= 3:
 break
 time.sleep(2)
 continue
 
 if not messages:
 print(f"0 messages | Stopping")
 break
 
 # Filter CFB
 batch_cfb = filter_cfb(messages)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 consecutive_empty += 1
 print(f"0 CFB | Total: {len(all_cfb)} | {elapsed:.1f}s")
 else:
 consecutive_empty = 0
 all_cfb.extend(batch_cfb)
 
 # Update last message ID (oldest in batch)
 if batch_cfb:
 # Messages are newest first, so last one is oldest
 last_id = batch_cfb[-1].get("id")
 
 print(f"{batch_size:2d} CFB ✅ | Total: {len(all_cfb)} | {elapsed:.1f}s")
 
 # Save immediately
 unique = save_messages(all_cfb)
 if len(unique) != len(all_cfb):
 print(f" (Removed {len(all_cfb) - len(unique)} duplicates)")
 
 # Cleanup
 temp_file.unlink(missing_ok=True)
 
 # Small delay to avoid rate limits
 time.sleep(0.3)
 
 except KeyboardInterrupt:
 print("\n\n⚠️ Interrupted by user")
 unique = save_messages(all_cfb)
 print(f"✅ Saved: {len(unique)} unique CFB messages from {batch_num} batches")
 return 0
 
 except Exception as e:
 print(f"\n❌ Error: {e}")
 import traceback
 traceback.print_exc()
 save_messages(all_cfb)
 return 1
 
 unique = save_messages(all_cfb)
 
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 print(f"Batches processed: {batch_num}")
 print(f"CFB messages found: {len(unique)}")
 print(f"Saved to: {MESSAGES_FILE}")
 print()
 
 if unique:
 print("Sample messages:")
 for i, msg in enumerate(unique[:3], 1):
 timestamp = msg.get("timestamp", "N/A")
 content = msg.get("content", "")[:80]
 print(f" {i}. [{timestamp}] {content}...")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

