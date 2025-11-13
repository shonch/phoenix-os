# autoparse.py — Phoenix Clipboard Ritual Parser (Canon Edition)
# Author: Shon Heersink & Copilot

import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path BEFORE importing phoenix_core
current_dir = os.path.dirname(__file__)
py_path = os.path.abspath(os.path.join(current_dir, "..", "py"))
sys.path.insert(0, py_path)

from phoenix_core import db

def get_clipboard():
    return os.popen("pbpaste").read()

def parse_frisson(log):
    print("\n✨ Parsing Frisson Entry from Clipboard")
    timestamp = re.search(r"# *Emotion Log: *(.*)", log, re.IGNORECASE)
    tags = re.search(r"# *Tag: *(.*)", log, re.IGNORECASE)
    entry = re.search(r"# *Entry: *(.*)", log, re.IGNORECASE)

    if not (timestamp and tags and entry):
        print("⚠️ Parsing failed. Please format clipboard like:")
        print("# Emotion Log: 2025-09-06 18:20")
        print("# Tag: grief, memory, Nadya")
        print("# Entry: Felt the ache of missed connection while folding laundry")
        return

    ts = timestamp.group(1).strip()
    tg = [t.strip() for t in tags.group(1).split(",")]
    en = entry.group(1).strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    md_content = f"""### ✨ Frisson Entry

**Logged**: {now}  
**Original Timestamp**: {ts}  
**Tags**: {", ".join(tg)}  
**Entry**: {en}
"""
    doc = {
        "timestamp": now,
        "type": "frisson_clipboard",
        "tags": tg + ["frisson", "clipboard"],
        "content": md_content,
        "note": f"Frisson parsed from clipboard ({ts})",
        "source": "autoparse.py"
    }
    result = db["emotional_fragments"].insert_one(doc)
    print(f"✅ Frisson entry logged to Phoenix — Fragment ID: {result.inserted_id}")

def parse_general(log):
    print("\n📝 Parsing General Note from Clipboard")
    folders = [
        "emotional_logs", "oslo_strategy", "phoenix_portfolio",
        "training_strategy", "resonance.sh", "cleansing", "rituals"
    ]
    print("📁 Choose symbolic folder tag:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    choice = input("Enter number or type custom tag: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(folders):
        folder_tag = folders[int(choice) - 1]
    elif choice:
        folder_tag = choice
    else:
        print("⚠️ No tag selected. Aborting.")
        return

    note_title = input("Note title: ").strip()
    note_tags = input("Tags (comma-separated): ").strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag_list = [t.strip() for t in note_tags.split(",")]

    md_content = f"""### 📝 General Note

**Title**: {note_title}  
**Logged**: {now}  
**Folder Tag**: {folder_tag}  
**Tags**: {", ".join(tag_list)}

{log}
"""
    doc = {
        "timestamp": now,
        "type": "general_clipboard",
        "tags": tag_list + [folder_tag, "clipboard"],
        "content": md_content,
        "note": f"General note '{note_title}' parsed from clipboard",
        "source": "autoparse.py"
    }
    result = db["emotional_fragments"].insert_one(doc)
    print(f"✅ General note logged to Phoenix — Fragment ID: {result.inserted_id}")

def run():
    load_dotenv()
    print("📋 Reading clipboard...")
    log = get_clipboard().strip()

    if not log:
        print("⚠️ Clipboard is empty. Aborting.")
        return

    note_type = input("Note type (frisson/general): ").strip().lower()
    if note_type == "frisson":
        parse_frisson(log)
    elif note_type == "general":
        parse_general(log)
    else:
        print("⚠️ Unknown note type. Aborting.")

# Optional: allow standalone execution
if __name__ == "__main__":
    run()
