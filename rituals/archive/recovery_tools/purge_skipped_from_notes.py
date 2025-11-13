# purge_skipped_from_notes.py — Final Ghost Sweep (Notes Edition)
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
    notes = doc.get("notes", "")
    if isinstance(notes, str):
        lines = notes.splitlines()
        cleaned_lines = [line for line in lines if not line.startswith(pattern)]
        new_notes = "\n".join(cleaned_lines)

        if new_notes != notes:
            collection.update_one({"_id": doc["_id"]}, {"$set": {"notes": new_notes}})
            print(f"🧹 Purged skipped echoes from notes in fragment {str(doc['_id'])[:6]}")
            count += 1

print(f"\n✅ Purged {count} fragments. Skipped echoes removed from notes field. Phoenix is clean.")
