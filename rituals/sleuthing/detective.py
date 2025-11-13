# detective.py — Emotional Sleuthing Protocol (Phoenix Mongo Edition)
# Author: Shon Heersink & Copilot

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path BEFORE importing phoenix_core
from rituals.utils.phoenix_paths import establish_phoenix_root
establish_phoenix_root()


def run():
    load_dotenv()
    print("🕵️‍♂️ Initiating emotional sleuthing sequence...")

    clue_type = input("Clue type (body, dream, glitch, longing): ").strip()
    location = input("Location (memory, Phoenix folder, terminal, dream): ").strip()
    status = input("Status (unresolved, echoing, integrated): ").strip()
    symbol = input("Symbol (song, scent, phrase, image): ").strip()
    note = input("Optional note: ").strip()
    weather = input("🌤️ Emotional weather (optional): ").strip()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 🔍 Tag suggestion logic
    raw_tags = [clue_type, location, status, symbol]
    final_tags = []

    for raw_tag in raw_tags:
        suggestions = suggest_tags(raw_tag)
        if suggestions:
            print(f"\n🔍 Suggestions for '{raw_tag}':")
            for i, tag in enumerate(suggestions):
                print(f"{i+1}. {tag['tag_name']} (used {tag.get('usage_count', 0)}x)")
            choice = input("Use a suggestion? Enter number or press Enter to keep original: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                final_tags.append(suggestions
