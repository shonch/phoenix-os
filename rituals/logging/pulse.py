# pulse.py — Phoenix Pulse Fragment Logger (Canon Edition)
# Author: Shon Heersink & Copilot

# pulse.py — Phoenix Pulse Fragment Logger (Canon Edition)
# Author: Shon Heersink & Copilot

import os
import sys
from datetime import datetime

# Patch sys.path BEFORE importing phoenix_core and backend

from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags

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
            "description": f"Auto-inserted from pulse.py",
            "dominatrix_affinity": []
        }
        create_tag(tag_data)

    return final_tags

def run():

    print("\n🌊 Pulse Fragment Logger")

    title = input("Enter title (e.g., uptown-runner): ").strip()
    emotion = input("Enter emotion (e.g., awe, longing): ").strip()
    tags = input("Enter tags (comma-separated): ").strip()

    print("Enter poetic fragment (multi-line, end with Ctrl+D):")
    fragment = sys.stdin.read().strip()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw_tags = [t.strip() for t in tags.split(",") if t.strip()]
    raw_tags += ["pulse", emotion]
    final_tags = suggest_and_normalize_tags(raw_tags)

    md_content = f"""### 🌊 Pulse Fragment

**Logged**: {timestamp}  
**Title**: {title}  
**Emotion**: {emotion}  
**Tags**: {", ".join(final_tags)}  

{fragment}
"""

    doc = {
    "timestamp": timestamp,
    "type": "pulse_fragment",
    "tags": final_tags,
    "title": title,
    "emotion": emotion,
    "logged": timestamp,
    "content": md_content,
    "raw_fragment": fragment,
    "note": f"Pulse fragment '{title}' logged with emotion: {emotion}",
    "source": "pulse.py"
}

    result = db["emotional_fragments"].insert_one(doc)
    print(f"✅ Pulse fragment logged to Phoenix — Fragment ID: {result.inserted_id}")

if __name__ == "__main__":
    run()
