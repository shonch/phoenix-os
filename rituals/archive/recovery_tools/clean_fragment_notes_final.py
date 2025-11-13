# clean_fragment_notes_final.py — Phoenix Echo Purge
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

def normalize_path(path):
    return os.path.abspath(os.path.expanduser(path.strip()))

# Sweep fragments
docs = collection.find({})
for doc in docs:
    notes = doc.get("notes", "")
    lines = notes.splitlines()
    cleaned_lines = []

    for line in lines:
        if line.startswith("❓ Unknown format skipped:"):
            raw_path = line.replace("❓ Unknown format skipped:", "").strip()
            normalized_path = normalize_path(raw_path)
            recovered = collection.find_one({
                "$or": [
                    {"source_path": normalized_path},
                    {"source_path": raw_path},
                    {"source_path": {"$regex": os.path.basename(raw_path)}}
                ],
                "fragment": "recovered"
            })
            if not recovered:
                cleaned_lines.append(line)  # Still skipped, keep it
        else:
            cleaned_lines.append(line)  # Keep all other notes

    new_notes = "\n".join(cleaned_lines)

    # Overwrite notes field
    collection.update_one({"_id": doc["_id"]}, {"$set": {"notes": new_notes}})
    print(f"🧹 Notes updated for fragment {str(doc['_id'])[:6]}")

print("\n✅ All fragment notes swept and overwritten. Skipped ghosts silenced.")
