# emotional_programming.py — Interactive Emotional Ritual Engine (Phoenix Edition)
# Author: Shon Heersink & Copilot

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path BEFORE importing phoenix_core
from rituals.utils.phoenix_paths import establish_phoenix_root
establish_phoenix_root()


from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags


def log_fragment(doc):
    result = db["emotional_fragments"].insert_one(doc)
    print(f"📁 Logged to Phoenix — Fragment ID: {result.inserted_id}")

def suggest_and_normalize_tags(raw_tags):
    final_tags = []
    for raw_tag in raw_tags:
        suggestions = suggest_tags(raw_tag)
        if suggestions:
            print(f"\n🔍 Suggestions for '{raw_tag}':")
            for i, tag in enumerate(suggestions):
                print(f"{i+1}. {tag['tag_name']} (used {tag.get('usage_count', 0)}x)")
            choice = input("Use a suggestion? Enter number or press Enter to keep original: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                final_tags.append(suggestions[int(choice)-1]["tag_name"])
            else:
                final_tags.append(normalize_tag(raw_tag))
        else:
            final_tags.append(normalize_tag(raw_tag))

    for tag in final_tags:
        tag_data = {
            "tag_name": tag,
            "emoji": "🌀",
            "archetype": "unclassified",
            "sass_level": 0,
            "emotional_weight": "neutral",
            "color": "#999999",
            "source_system": "phoenix",
            "description": f"Auto-inserted from emotional_programming.py",
            "dominatrix_affinity": []
        }
        create_tag(tag_data)

    return final_tags

def trace_frisson():
    print("\n✨ Trace Frisson")
    location = input("Where were you? ").strip()
    song = input("What song or sound triggered it? ").strip()
    feeling = input("What did it feel like? ").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    raw_tags = ["frisson", "trace", song, feeling]
    final_tags = suggest_and_normalize_tags(raw_tags)

    md_content = f"""### ✨ Frisson Trace

**Timestamp**: {timestamp}  
**Location**: {location}  
**Song**: {song}  
**Feeling**: {feeling}
"""
    doc = {
        "timestamp": timestamp,
        "type": "frisson_trace",
        "tags": final_tags,
        "content": md_content,
        "note": "Frisson trace logged with emotional detail.",
        "source": "emotional_programming.py"
    }
    log_fragment(doc)

def archive_grief():
    print("\n🕊️ Archive Grief")
    source = input("What memory or symbol are you archiving? ").strip()
    reflection = input("Optional reflection: ").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    raw_tags = ["grief", "archive", source]
    final_tags = suggest_and_normalize_tags(raw_tags)

    md_content = f"""### 🕊️ Grief Archive

**Symbolic Archive**: {source}  
**Timestamp**: {timestamp}  
{f"**Reflection**: {reflection}" if reflection else ""}
"""
    doc = {
        "timestamp": timestamp,
        "type": "grief_archive",
        "tags": final_tags,
        "content": md_content,
        "note": "Symbolic grief archive logged.",
        "source": "emotional_programming.py"
    }
    log_fragment(doc)

def tag_emotion():
    print("\n🏷️ Tag Emotion")
    options = {
        "1": "💫 awe",
        "2": "🧊 detachment",
        "3": "🔥 urgency",
        "4": "🌿 restoration",
        "5": "🪨 grounding",
        "6": "🌀 confusion",
        "7": "✍️ custom"
    }
    for key, val in options.items():
        print(f"{key}. {val}")
    choice = input("Choose an emotion to tag [1–7]: ").strip()

    if choice == "7":
        tag = input("Enter your custom emotion tag: ").strip()
    else:
        tag = options.get(choice, "🌫️ unknown")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw_tags = ["emotion", "tag", tag]
    final_tags = suggest_and_normalize_tags(raw_tags)

    md_content = f"""### 🏷️ Emotion Tag

**Tag**: {tag}  
**Timestamp**: {timestamp}
"""
    doc = {
        "timestamp": timestamp,
        "type": "emotion_tag",
        "tags": final_tags,
        "content": md_content,
        "note": f"Emotion tagged: {tag}",
        "source": "emotional_programming.py"
    }
    log_fragment(doc)

def clean_legacy():
    print("\n🧹 Clean Legacy")
    structure = input("What outdated structure or belief are you clearing? ").strip()
    note = input("Optional reflection or note: ").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    raw_tags = ["legacy", "cleanup", structure]
    final_tags = suggest_and_normalize_tags(raw_tags)

    md_content = f"""### 🧹 Legacy Cleanup

**Symbolic Structure Removed**: {structure}  
**Timestamp**: {timestamp}  
{f"**Note**: {note}" if note else ""}
"""
    doc = {
        "timestamp": timestamp,
        "type": "legacy_cleanup",
        "tags": final_tags,
        "content": md_content,
        "note": f"Legacy cleanup: {structure}" + (f" — {note}" if note else ""),
        "source": "emotional_programming.py"
    }
    log_fragment(doc)

def restore_sanctuary():
    print("\n🏕️ Restore Sanctuary")
    intention = input("What intention are you restoring sanctuary for? ").strip()
    disruption = input("What disrupted your sanctuary? ").strip()
    method = input("What are you doing to restore it? ").strip()
    reflection = input("Optional reflection or vow: ").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    raw_tags = ["sanctuary", "restore", "ritual", intention, disruption]
    final_tags = suggest_and_normalize_tags(raw_tags)

    md_content = f"""### 🏕️ Sanctuary Restoration

**Timestamp**: {timestamp}  
**Intention**: {intention}  
**Disruption**: {disruption}  
**Restoration Method**: {method}  
{f"**Reflection**: {reflection}" if reflection else ""}
"""
    doc = {
        "timestamp": timestamp,
        "type": "sanctuary_restore",
        "tags": final_tags,
        "content": md_content,
        "note": f"Sanctuary restored for: {intention}",
        "source": "emotional_programming.py"
    }
    log_fragment(doc)

def run():
    load_dotenv()
    print("\n🛠️ Emotional Programming Rituals")
    print("Choose your ritual:")
    print("1. Trace Frisson")
    print("2. Archive Grief")
    print("3. Tag Emotion")
    print("4. Clean Legacy")
    print("5. Restore Sanctuary")
    choice = input("Enter choice [1–5]: ").strip()

    if choice == "1": trace_frisson()
    elif choice == "2": archive_grief()
    elif choice == "3": tag_emotion()
    elif choice == "4": clean_legacy()
    elif choice == "5": restore_sanctuary()
    else: print("⚠️ Invalid choice. Ritual not performed.")

if __name__ == "__main__":
    run()
