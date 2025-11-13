# valhalla_tracker.py — Phoenix Module Status Ritual
# Author: Shon Heersink & Copilot

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Patch sys.path to reach phoenix_core.py


load_dotenv()
from backend.mongo_client import db

def insert_row(collection_name, data):
    db[collection_name].insert_one(data)

def select_rows(collection_name, query):
    return list(db[collection_name].find(query))

def update_row(collection_name, query, update):
    db[collection_name].update_one(query, {"$set": update})

def log_module_status(module_name, status, needs_validation, emotional_flow, notes=""):
    entry = {
        "module_name": module_name,
        "status": status,
        "needs_validation": needs_validation,
        "emotional_flow": emotional_flow,
        "notes": notes,
        "timestamp": datetime.utcnow().isoformat()
    }

    existing = select_rows("module_status", {"module_name": module_name})
    if existing:
        update_row("module_status", {"module_name": module_name}, entry)
        print(f"🔄 Updated {module_name} in Valhalla Tracker.")
    else:
        insert_row("module_status", entry)
        print(f"📘 Logged {module_name} to Valhalla Tracker.")

def view_tracker():
    modules = select_rows("module_status", {})
    modules = sorted(modules, key=lambda x: x["module_name"])

    print("\n📊 Valhalla Tracker Overview:")
    for mod in modules:
        print(f"• {mod['module_name']}: {mod['status']} | Validation: {'✅' if mod['needs_validation'] else '❌'} | Emotional Flow: {'🌊' if mod['emotional_flow'] else '—'}")
        print(f"  ↳ Last Reviewed: {mod.get('timestamp', 'N/A')}")
        if mod.get("notes"):
            print(f"  ↳ Notes: {mod['notes']}")
def run():
    print("\n📜 Valhalla Tracker")
    print("Choose your ritual:")
    print("1. View Tracker")
    print("2. Log a Module")
    choice = input("Enter choice [1–2]: ").strip()

    if choice == "1":
        view_tracker()
    elif choice == "2":
        print("\n📝 Log Module Status")
        module_name = input("Module name (e.g., log_emotion.py): ").strip()
        status = input("Status [Active / Partial / Dormant]: ").strip()
        needs_validation = input("Needs validation? [y/n]: ").strip().lower() == "y"
        emotional_flow = input("Emotional flow present? [y/n]: ").strip().lower() == "y"
        notes = input("Optional notes: ").strip()

        log_module_status(module_name, status, needs_validation, emotional_flow, notes)
    else:
        print("⚠️ Invalid choice. Ritual not performed.")
