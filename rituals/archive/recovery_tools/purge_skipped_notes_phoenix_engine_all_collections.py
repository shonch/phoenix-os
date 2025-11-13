# purge_skipped_notes_backend_all_collections.py — Final Ghost Sweep Across All Collections
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["backend"]

# Get all collections
collections = db.list_collection_names()
pattern = "❓ Unknown format skipped:"
total_purged = 0

for name in collections:
    collection = db[name]
    docs = collection.find({})
    count = 0

    for doc in docs:
        notes = doc.get("notes", "")
        if isinstance(notes, str):
            lines = notes.splitlines()
            cleaned_lines = [line for line in lines if not line.startswith(pattern)]
            new_notes = "\n".join(cleaned_lines)

            if new_notes != notes:
                collection.update_one({"_id": doc["_id"]}, {"$set": {"notes": new_notes}})
                print(f"🧹 Purged from {name} → fragment {str(doc['_id'])[:6]}")
                count += 1

    if count:
        print(f"✅ Purged {count} fragments from collection '{name}'")
        total_purged += count

print(f"\n🧼 Final sweep complete. Total purged fragments: {total_purged}")
