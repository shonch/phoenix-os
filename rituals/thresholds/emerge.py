# emerge.py — Unconscious Revelation Logger (Phoenix Edition)
# Author: Shon Heersink & Copilot
# Purpose: Capture moments when something surfaces that was always there.

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path BEFORE importing phoenix_core

from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags

def run():
    load_dotenv()
    print("🌱 Emerge protocol initiated...")

    rev_type = input("Revelation type (identity, grief, pattern, longing): ").strip()
    trigger = input("Symbol or trigger (dream, phrase, memory): ").strip()
    reflection = input("Optional reflection: ").strip()
    weather = input("🌤️ Emotional weather (optional): ").strip()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 🔍 Tag suggestion logic
    raw_tags = [rev_type, trigger, "emerge"]
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
            "description": f"Auto-inserted from emerge.py",
            "dominatrix_affinity": []
        }
        create_tag(tag_data)

    md_content = f"""### 🌱 Unconscious Revelation

**Type**: {rev_type}  
**Trigger**: {trigger}  
**Weather**: {weather}  
**Timestamp**: {timestamp}  

---

{reflection}
"""

    doc = {
        "subject": f"Revelation: {rev_type}",
        "tags": final_tags,
        "weather": weather,
        "content": md_content,
        "date": timestamp,
        "source": "emerge.py"
    }
    db["revelations"].insert_one(doc)

    print("🧠 Revelation logged to Phoenix database (revelations collection).")
    input("\n🔚 Press Enter to return to the Phoenix console...")

if __name__ == "__main__":
    run()
