# tag_manager.py — Phoenix Symbolic Tag Ritual (Expanded Listing Edition)
# Author: Shon Heersink & Copilot

import sys
from datetime import datetime
from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, list_tags, normalize_tag, update_tag

def run():
    print("\n🔮 Symbolic Tag Ritual — Manage Emotional Overlays")

    raw_tag = input("Enter a tag name (e.g., grounded_indulgence): ").strip()
    if not raw_tag:
        print("⚠️ No tag entered. Ritual aborted.")
        return

    normalized = normalize_tag(raw_tag)

    tag_doc = {
        "tag_name": normalized,
        "emoji": "🌀",
        "archetype": "unclassified",
        "emotional_weight": "neutral",
        "color": "#999999",
        "source_system": "phoenix",
        "description": "Inserted via Symbolic Tag Ritual",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    result = db["tag_index"].insert_one(tag_doc)
    print(f"✅ Tag '{normalized}' logged to Phoenix tag_index — ID: {result.inserted_id}")

    update_choice = input("Update existing tag metadata? (y/n): ").strip().lower()
    if update_choice == "y":
        new_description = input("Enter description: ").strip()
        new_weight = input("Enter emotional weight (comfort, survival, sovereignty, expansion): ").strip()
        new_archetype = input("Enter archetype (e.g., indulgence, resilience, clarity): ").strip()
        new_color = input("Enter hex color (e.g., #ffcc66): ").strip()

        update_fields = {}
        if new_description:
            update_fields["description"] = new_description
        if new_weight:
            update_fields["emotional_weight"] = new_weight
        if new_archetype:
            update_fields["archetype"] = new_archetype
        if new_color:
            update_fields["color"] = new_color

        if update_fields:
            update_tag(normalized, update_fields)
            print(f"🔄 Tag '{normalized}' updated with metadata: {update_fields}")
        else:
            print("⚠️ No metadata entered. Tag remains neutral.")

    # Expanded listing output
    print("\n📂 Current Tags in tag_index:")
    for tag in list_tags():
        print(
            f"- {tag['tag_name']} "
            f"(weight: {tag.get('emotional_weight', 'neutral')}, "
            f"archetype: {tag.get('archetype', 'none')}, "
            f"description: {tag.get('description', '')}, "
            f"color: {tag.get('color', '')})"
        )

if __name__ == "__main__":
    run()
