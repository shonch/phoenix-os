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

# Sweep fragments
docs = collection.find({})
for doc in docs:
    notes = doc.get("notes", "")
    lines = notes.splitlines()
    recovered_paths = []
    skipped_paths = []
    other_notes = []

    for line in lines:
        if line.startswith("❓ Unknown format skipped:"):
            skipped_path = line.replace("❓ Unknown format skipped:", "").strip()
            normalized_path = os.path.abspath(skipped_path)
            recovered = collection.find_one({"source_path": normalized_path, "fragment": "recovered"})
            if recovered:
                recovered_paths.append(normalized_path)
            else:
                skipped_paths.append(normalized_path)
        else:
            other_notes.append(line)

    # Rebuild notes field
    new_notes = ""
    if recovered_paths:
        new_notes += "🛡️ Recovered fragments:\n" + "\n".join(f"- {p}" for p in recovered_paths) + "\n"
    if skipped_paths:
        new_notes += "⚠️ Still skipped:\n" + "\n".join(f"- {p}" for p in skipped_paths) + "\n"
    if other_notes:
        new_notes += "\n".join(other_notes)

    # Update document if notes changed
    if new_notes.strip() != notes.strip():
        collection.update_one({"_id": doc["_id"]}, {"$set": {"notes": new_notes}})
        print(f"🧹 Cleaned notes for fragment {str(doc['_id'])[:6]}")

print("\n✅ All fragment notes swept and updated.")
