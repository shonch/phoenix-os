# threshold_guard.py — Emotional Threshold Protection (Phoenix Mongo Edition)
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
    print("🛡️ Scanning emotional threshold integrity...")

    threshold_type = input("Threshold type (grief, fatigue, legacy, trust): ").strip()
    status = input("Status (stable, fragile, breached): ").strip().lower()
    anchor = normalize_tag(anchor.strip())
    weather = input("🌤️ Emotional weather (optional): ").strip()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 🔍 Tag suggestion logic
    raw_tags = [threshold_type, status, anchor]
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

    md_content = f"""### 🛡️ Threshold Scan

**Type**: {threshold_type}  
**Status**: {status}  
**Anchor**: {anchor}  
**Weather**: {weather}  
**Timestamp**: {timestamp}  
"""
emotional_weight = "heavy" if status == "breached" else "neutral"
    for tag in final_tags:
        tag_data = {
            "tag_name": tag,
            "emoji": "🌀",
            "archetype": "unclassified",
            "sass_level": 0,
            "emotional_weight": emotional_weight,            
            "color": "#999999",
            "source_system": "phoenix",
            "description": f"Auto-inserted from threshold_guard.py",
            "dominatrix_affinity": []
        }
        create_tag(tag_data)

    doc = {
        "subject": f"Threshold: {threshold_type}",
        "tags": final_tags,
        "weather": weather,
        "content": md_content,
        "date": timestamp,
        "source": "threshold_guard.py"
    }
    db["thresholds"].insert_one(doc)

    print("\n🔐 Threshold Scan Logged:")
    print(md_content)
    print("🧠 Saved to Phoenix database (thresholds collection).")

    if status in ["fragile", "breached"]:
        print(f"🕯️ Ritual pause required. Anchor with: {anchor}")
        print("📁 Threshold breach logged. Consider invoking grind_protocol.py if needed.")
    else:
        print("✅ Threshold stable. Proceed with care.")

    input("\n🔚 Press Enter to return to the Phoenix console...")

if __name__ == "__main__":
    run()
