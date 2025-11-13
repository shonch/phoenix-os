# purge_skipped_from_notes_list.py — Final Ghost Sweep (List Edition)
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

# Sweep and purge
docs = collection.find({})
count = 0
pattern = "❓ Unknown format skipped:"

for doc in docs:
    notes = doc.get("notes", [])
    if isinstance(notes, list):
        cleaned_notes = [line for line in notes if not line.startswith(pattern)]

        if cleaned_notes != notes:
            collection.update_one({"_id": doc["_id"]}, {"$set": {"notes": cleaned_notes}})
            print(f"🧹 Purged skipped echoes from notes list in fragment {str(doc['_id'])[:6]}")
            count += 1

print(f"\n✅ Purged {count} fragments. Skipped echoes removed from notes list. Phoenix is clean.")
