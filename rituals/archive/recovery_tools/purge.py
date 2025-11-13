from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["fragments"]

# Sweep and purge
docs = collection.find({})
for doc in docs:
    notes = doc.get("notes", "")
    lines = notes.splitlines()
    cleaned_lines = [line for line in lines if not line.startswith("❓ Unknown format skipped:")]
    new_notes = "\n".join(cleaned_lines)

    # Overwrite notes field
    collection.update_one({"_id": doc["_id"]}, {"$set": {"notes": new_notes}})
    print(f"🧹 Purged skipped echoes from fragment {str(doc['_id'])[:6]}")

print("\n✅ All skipped echoes removed. Phoenix is clean.")
