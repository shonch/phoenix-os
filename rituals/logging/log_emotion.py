# log_emotion.py — Global emotional changelog logger (Phoenix Mongo Edition)
# Author: Shon Heersink & Copilot

import os
import sys
import subprocess
from datetime import datetime

from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags

def save_to_phoenix(message, tags, weather, md_content, timestamp):
    normalized_tags = [normalize_tag(t.strip()) for t in tags.split(',')]    
    
for tag in normalized_tags:
    tag_data = {
        "tag_name": tag,
        "title": tag.replace("_", " ").title(),  # Add human-readable title
        "emoji": "🌀",
        "archetype": "unclassified",
        "sass_level": 0,
        "emotional_weight": "neutral",
        "color": "#999999",
        "source_system": "phoenix",
        "description": "Auto-inserted from log_emotion.py",
        "dominatrix_affinity": [],
        "created_at": datetime.utcnow().isoformat()
    }
    create_tag(tag_data)

    doc = {
        "subject": message,
        "tags": normalized_tags,
        "weather": weather,
        "content": md_content,
        "date": timestamp,
        "source": "log_emotion.py"
    }
    db["fragments"].insert_one(doc)
    print("🧠 Logged to Phoenix database.")

def run():
    message = input("📝 What are you logging today?\n> ")
    tags = input("🏷️ Enter tags (space-separated):\n> ")
    weather = input("🌤️ Emotional weather (e.g., lucid, foggy, volatile):\n> ")

    raw_tags = tags.split()
    final_tags = []

    for raw_tag in raw_tags:
        normalized = normalize_tag(raw_tag)
        suggestions = suggest_tags(normalized)
        print(f"🧪 Suggestions for '{normalized}': {suggestions}")  # Debug line

        if suggestions:
            print(f"\n🔍 Suggestions for '{raw_tag}':")
            for i, tag in enumerate(suggestions):
                print(f"{i+1}. {tag['tag_name']} (used {tag.get('usage_count', 0)}x)")
            choice = input("Use a suggestion? Enter number or press Enter to keep original: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                final_tags.append(suggestions[int(choice)-1]["tag_name"])
            else:
                final_tags.append(normalized)
        else:
            final_tags.append(normalized)

    temp_notes = os.path.expanduser("~/.emotion_notes_tmp.md")
    print("🖋️ Opening Vim for notes... (save and quit to continue)")
    subprocess.call(["vim", temp_notes])
    with open(temp_notes, "r") as f:
        notes = f.read()
    os.remove(temp_notes)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    md_content = f"""### 📜 Emotion Log

**Subject**: {message}  
**Tags**: {" ".join(final_tags)}  
**Weather**: {weather}  
**Timestamp**: {timestamp}  

{notes}
"""

    save_to_phoenix(message, " ".join(final_tags), weather, md_content, timestamp)

    formatted_tags = "`" + "` `".join(final_tags) + "`"
    entry = f"\n---\n## ENTRY START\n**{timestamp}**\n{message}\nTag: {formatted_tags}\nWeather: *{weather}*\nNotes:\n{notes}\n## ENTRY END\n"
    print(entry)

if __name__ == "__main__":
    run()
