# tag_manager.py — Symbolic Tag Ritual CLI
# Author: Shon Heersink & Copilot

import sys
import os
from pprint import pprint

# Add phoenix_portfolio to sys.path
from rituals.utils.phoenix_paths import establish_phoenix_root
establish_phoenix_root()

from phoenix_core import create_tag, list_tags, normalize_tag, update_tag

def run():
    print("\n🧠 Symbolic Tag Ritual — Manage Emotional Overlays")
    print("1. Create a new symbolic tag")
    print("2. List all symbolic tags")
    print("3. Update an existing tag")
    choice = input("Choose an option [1–3]: ").strip()

    if choice == "1":
        tag_name = input("Tag name: ")
        tag_data = {
            "tag_name": normalize_tag(tag_name),
            "emoji": input("Emoji: "),
            "archetype": input("Archetype (e.g. guardian, rebel): "),
            "sass_level": int(input("Sass level (0–10): ")),
            "emotional_weight": input("Emotional weight (light, heavy, volatile): "),
            "color": input("Color (hex code): "),
            "source_system": "phoenix",
            "description": input("Description: "),
            "dominatrix_affinity": [t.strip() for t in input("Dominatrix affinity (comma-separated): ").split(",") if t.strip()]
        }
        tag_id = create_tag(tag_data)
        print(f"\n✅ Tag created with ID: {tag_id}")

    elif choice == "2":
        tags = list_tags()
        print(f"\n📜 Total tags: {len(tags)}")
        for tag in tags:
            pprint(tag)

    elif choice == "3":
        tag_id = input("Enter tag ID to edit: ")
        field = input("Field to update (e.g. emoji, sass_level): ")
        value = input("New value: ")
        updates = {field: value}
        success = update_tag(tag_id, updates)
        print("✅ Tag updated." if success else "⚠️ Tag not found or unchanged.")

    else:
        print("⚠️ Invalid choice. Ritual not performed.")

if __name__ == "__main__":
    run()
