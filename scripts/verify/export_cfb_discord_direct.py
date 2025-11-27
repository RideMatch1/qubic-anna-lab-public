#!/usr/bin/env python3
"""
Direct CFB Discord Message Exporter - Uses DiscordChatExporter directly with live output
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread
from queue import Queue

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092"

# Paths
EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

def stream_output(pipe, queue):
 """Stream output from subprocess to queue."""
 try:
 for line in iter(pipe.readline, ''):
 if line:
 queue.put(line)
 pipe.close()
 except Exception:
 pass
 finally:
 queue.put(None)

def export_channel_json(
 token: str,
 channel_id: str,
 output_file: Path,
 after: Optional[str] = None,
) -> tuple[bool, str]:
 """Export channel with live output streaming."""
 if not EXPORTER_PATH.exists():
 return False, f"DiscordChatExporter.Cli not found"
 
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
 print(" [Exporting...]", end="", flush=True)
 
 process = subprocess.Popen(
 cmd,
 stdout=subprocess.PIPE,
 stderr=subprocess.STDOUT,
 text=True,
 bufsize=1,
 )
 
 # Stream output
 queue = Queue()
 thread = Thread(target=stream_output, args=(process.stdout, queue))
 thread.daemon = True
 thread.start()
 
 # Print output as it comes
 dots = 0
 while True:
 try:
 line = queue.get(timeout=0.5)
 if line is None:
 break
 if line.strip():
 print(f"\n {line.strip()}", flush=True)
 dots = 0
 else:
 dots += 1
 if dots % 10 == 0:
 print(".", end="", flush=True)
 except:
 # Check if process is still running
 if process.poll() is not None:
 break
 print(".", end="", flush=True)
 time.sleep(0.1)
 
 thread.join(timeout=1)
 process.wait()
 
 if process.returncode == 0:
 print("\n ✅ Export complete", flush=True)
 return True, ""
 else:
 return False, f"Exit code: {process.returncode}"
 
 except subprocess.TimeoutExpired:
 return False, "Timeout"
 except Exception as e:
 return False, str(e)

def filter_cfb_messages(json_file: Path) -> list:
 """Filter CFB messages."""
 if not json_file.exists() or json_file.stat().st_size == 0:
 return []
 
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 if "messages" in data:
 for msg in data["messages"]:
 if msg.get("author", {}).get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 except Exception as e:
 print(f" ⚠️ Error: {e}")
 return []

def load_existing_messages() -> list:
 """Load existing messages."""
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
 """Main function."""
 print("=" * 80)
 print("🚀 DIRECT CFB DISCORD EXPORTER (LIVE OUTPUT)")
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
 
 all_messages = load_existing_messages()
 last_message_id = all_messages[-1].get("id") if all_messages else None
 
 if all_messages:
 print(f"📥 Resuming: {len(all_messages)} messages already saved")
 if last_message_id:
 print(f"📌 From message: {last_message_id}")
 else:
 print("📥 Starting new export...")
 
 print()
 print("Starting export (Ctrl+C to stop)...")
 print()
 
 batch_num = 0
 
 try:
 while True:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}.json"
 
 print(f"\n{'='*60}")
 print(f"Batch {batch_num}")
 print(f"{'='*60}")
 
 success, error = export_channel_json(
 token=token,
 channel_id=CHANNEL_ID,
 output_file=temp_file,
 after=last_message_id,
 )
 
 if not success:
 print(f"\n❌ Export failed: {error}")
 break
 
 print("\n [Filtering CFB messages...] ", end="", flush=True)
 batch_cfb = filter_cfb_messages(temp_file)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 print(f"0 CFB messages")
 
 # Check if done
 try:
 with temp_file.open(encoding="utf-8") as f:
 data = json.load(f)
 if not data.get("messages"):
 print(" ✅ No more messages")
 break
 except Exception:
 pass
 else:
 print(f"{batch_size} CFB messages found! ✅")
 all_messages.extend(batch_cfb)
 
 if batch_cfb:
 last_message_id = batch_cfb[-1].get("id")
 
 save_messages(all_messages)
 print(f" 💾 Total saved: {len(all_messages)} CFB messages")
 
 temp_file.unlink(missing_ok=True)
 
 if batch_size == 0:
 print("\n ⏸️ No CFB messages, stopping")
 break
 
 time.sleep(0.5)
 
 except KeyboardInterrupt:
 print("\n\n⚠️ Interrupted")
 print(f"✅ Saved: {len(all_messages)} messages")
 save_messages(all_messages)
 return 0
 
 except Exception as e:
 print(f"\n❌ Error: {e}")
 import traceback
 traceback.print_exc()
 save_messages(all_messages)
 return 1
 
 save_messages(all_messages)
 
 print()
 print("=" * 80)
 print("✅ COMPLETE")
 print("=" * 80)
 print(f"Batches: {batch_num}")
 print(f"CFB Messages: {len(all_messages)}")
 print(f"File: {MESSAGES_FILE}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

