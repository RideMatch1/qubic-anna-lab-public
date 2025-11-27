#!/usr/bin/env python3
"""
Fast CFB Export - 100 Messages per Batch, Only CFB Messages Saved

Works like the previous fast method: 100 messages per batch, filter CFB, save immediately.
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
BATCH_SIZE = 100 # Messages per batch

# Paths
EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

def export_batch(token: str, channel_id: str, output_file: Path, after: str = None, limit: int = 100) -> bool:
 """Export a small batch of messages."""
 if not EXPORTER_PATH.exists():
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
 
 # Use partition to limit batch size
 cmd.extend(["--partition", str(limit)])
 
 try:
 result = subprocess.run(
 cmd,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True,
 timeout=60, # 1 minute max per batch
 )
 return result.returncode == 0
 except subprocess.TimeoutExpired:
 return False
 except Exception:
 return False

def filter_cfb_messages(json_file: Path) -> list:
 """Extract only CFB messages."""
 if not json_file.exists():
 return []
 
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 for msg in data.get("messages", []):
 if msg.get("author", {}).get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 except Exception:
 return []

def load_existing() -> tuple[list, str]:
 """Load existing messages and last message ID."""
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
 """Save messages."""
 with MESSAGES_FILE.open("w", encoding="utf-8") as f:
 json.dump(messages, f, indent=2, ensure_ascii=False)

def main() -> int:
 """Main function - fast batch export."""
 print("=" * 80)
 print("🚀 FAST CFB EXPORT - 100 Messages per Batch")
 print("=" * 80)
 print()
 
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN not set!")
 return 1
 
 print(f"✅ Token: {token[:20]}...")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB ID: {CFB_USER_ID}")
 print(f"📦 Batch size: {BATCH_SIZE} messages")
 print()
 
 # Load existing
 all_cfb, last_id = load_existing()
 if all_cfb:
 print(f"📥 Resuming: {len(all_cfb)} CFB messages already saved")
 print(f"📌 Last message ID: {last_id}")
 else:
 print("📥 Starting new export...")
 
 print()
 print("Starting fast batch export (Ctrl+C to stop)...")
 print()
 
 batch_num = 0
 consecutive_empty = 0
 
 try:
 while True:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}.json"
 
 print(f"Batch {batch_num:3d} | ", end="", flush=True)
 
 # Export batch
 start_time = time.time()
 success = export_batch(token, CHANNEL_ID, temp_file, after=last_id, limit=BATCH_SIZE)
 elapsed = time.time() - start_time
 
 if not success:
 print(f"❌ Export failed ({elapsed:.1f}s)")
 break
 
 # Filter CFB
 batch_cfb = filter_cfb_messages(temp_file)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 consecutive_empty += 1
 print(f"0 CFB | Total: {len(all_cfb)} | {elapsed:.1f}s")
 
 # Check if done
 try:
 with temp_file.open(encoding="utf-8") as f:
 data = json.load(f)
 if not data.get("messages"):
 print(" ✅ No more messages")
 break
 except Exception:
 pass
 
 if consecutive_empty >= 5:
 print(" ⏸️ No CFB in last 5 batches, stopping")
 break
 else:
 consecutive_empty = 0
 all_cfb.extend(batch_cfb)
 
 # Update last message ID
 if batch_cfb:
 last_id = batch_cfb[-1].get("id")
 
 print(f"{batch_size:2d} CFB ✅ | Total: {len(all_cfb)} | {elapsed:.1f}s")
 
 # Save immediately
 save_messages(all_cfb)
 
 # Cleanup
 temp_file.unlink(missing_ok=True)
 
 # Small delay
 time.sleep(0.2)
 
 except KeyboardInterrupt:
 print("\n\n⚠️ Interrupted")
 print(f"✅ Saved: {len(all_cfb)} CFB messages from {batch_num} batches")
 save_messages(all_cfb)
 return 0
 
 except Exception as e:
 print(f"\n❌ Error: {e}")
 save_messages(all_cfb)
 return 1
 
 save_messages(all_cfb)
 
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 print(f"Batches: {batch_num}")
 print(f"CFB Messages: {len(all_cfb)}")
 print(f"File: {MESSAGES_FILE}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

