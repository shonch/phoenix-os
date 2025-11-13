# anti_grind.py — Grind Override Protocol (Phoenix Enhanced Edition)
# Author: Shon Heersink & Copilot

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path BEFORE importing phoenix_core

from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags

def run():
    load_dotenv()
    print("🧭 Anti-Grind Protocol Activated\n")

    signal = input("Current grind signal (fog, impulse, shutdown): ").strip().lower()
    action = input("Desired recalibration (pause, playlist, log, walk): ").strip().lower()
    weather = input("🌤️ Emotional weather (optional): ").strip()

    print(f"\n🛠️ Recalibrating with: {action}")
    print("🕯️ Grind is not legacy. Ritual override complete.")

    log = input("\nWould you like to log this override to Phoenix? (yes/no): ").strip().lower()
    if log == "yes":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 🔍 Tag suggestion logic
        raw_tags = [signal, action, "grind_override"]
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

        # Insert symbolic tags
        for tag in final_tags:
            tag_data = {
                "tag_name": tag,
                "emoji": "🌀",
                "archetype": "unclassified",
                "sass_level": 0,
                "emotional_weight": "neutral",
                "color": "#999999",
                "source_system": "phoenix",
                "description": f"Auto-inserted from anti_grind.py",
                "dominatrix_affinity": []
            }
            create_tag(tag_data)

        md_content = f"""### ⛔ Anti-Grind Override

**Signal**: {signal}  
**Action**: {action}  
**Weather**: {weather}  
**Timestamp**: {timestamp}  
"""

        db["emotional_fragments"].insert_one({
            "timestamp": timestamp,
            "type": "grind_override",
            "signal": signal,
            "action": action,
            "weather": weather,
            "tags": final_tags,
            "content": md_content,
            "note": "Grind override protocol activated.",
            "source": "anti_grind.py"
        })
        print("📁 Logged to backend.emotional_fragments")
    else:
        print("🛑 Override not logged. Ritual honored locally.")

    input("\n🔚 Press Enter to return to the Phoenix console...")

if __name__ == "__main__":
    run()
