# grind_protocol.py — Emotional Fatigue Detector (Phoenix Edition)
# Author: Shon Heersink & Copilot
# Purpose: Detect grind signals and initiate decompression rituals.

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path BEFORE importing phoenix_core

from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags

def run():
    load_dotenv()
    print("⚠️ Grind signal detected. Initiating protocol...\n")

    energy = int(input("Energy level (1-10): ").strip())
    sleep = input("Sleep quality (poor, okay, deep): ").strip().lower()
    state = input("Emotional state (foggy, anxious, numb, tender): ").strip().lower()
    urgency = input("Urgency to quit something (yes/no): ").strip().lower()

    if energy <= 4 or sleep == "poor" or urgency == "yes":
        print("\n🛑 No decisions for 24 hours. Ritual pause initiated.")
        print("🎧 Play decompression playlist. 🕯️ Log emotion. 📝 Archive impulse.")
        status = "pause"
    else:
        print("\n✅ No grind detected. Proceed with sovereignty.")
        status = "clear"

    log = input("\nWould you like to log this grind scan to Phoenix? (yes/no): ").strip().lower()
    if log == "yes":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 🔍 Tag suggestion logic
        raw_tags = [state, sleep, status, "grind_scan"]
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
                "description": f"Auto-inserted from grind_protocol.py",
                "dominatrix_affinity": []
            }
            create_tag(tag_data)

        md_content = f"""### ⚠️ Grind Protocol Scan

**Energy Level**: {energy}  
**Sleep Quality**: {sleep}  
**Emotional State**: {state}  
**Urgency to Quit**: {urgency}  
**Status**: {status}  
**Timestamp**: {timestamp}  
"""

        db["emotional_fragments"].insert_one({
            "timestamp": timestamp,
            "type": "grind_scan",
            "energy": energy,
            "sleep": sleep,
            "state": state,
            "urgency": urgency,
            "status": status,
            "tags": final_tags,
            "content": md_content,
            "note": "Grind protocol scan completed.",
            "source": "grind_protocol.py"
        })
        print("📁 Logged to backend.emotional_fragments")
    else:
        print("🛑 Scan not logged. Ritual honored locally.")

    input("\n🔚 Press Enter to return to the Phoenix console...")

if __name__ == "__main__":
    run()
