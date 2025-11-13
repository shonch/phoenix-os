# phoenix_fragment_cleaner.py — Remove Skipped Note from Original Fragment
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Target fragment and path to remove
fragment_id = ObjectId("68f7d2391a5c0c06e3d90203")
skipped_path = "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-31-evening-release.md"
skipped_line = f"- ❓ Unknown format skipped: {skipped_path}\n"

# Fetch and update
original = collection.find_one({"_id": fragment_id})
if original and "notes" in original:
    updated_notes = original["notes"].replace(skipped_line, "")
    collection.update_one({"_id": fragment_id}, {"$set": {"notes": updated_notes}})
    print("✅ Skipped note removed.")
else:
    print("⚠️ Original fragment not found or missing notes.")
