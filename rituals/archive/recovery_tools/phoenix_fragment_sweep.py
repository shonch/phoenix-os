# phoenix_fragment_sweep.py — Batch Verifier & Cleaner
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import re

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Target fragment with skipped notes
cluster_id = ObjectId("68f7d2391a5c0c06e3d90203")
cluster = collection.find_one({"_id": cluster_id})

if not cluster or "notes" not in cluster:
    print("⚠️ Skipped cluster not found or missing notes.")
    exit()

notes = cluster["notes"]
skipped_paths = re.findall(r"- ❓ Unknown format skipped: (.+)", notes)

print(f"🔍 Found {len(skipped_paths)} skipped paths.\n")

for path in skipped_paths:
    # Check for recovered fragment
    recovered = collection.find_one({
        "source_path": path.strip(),
        "fragment": "recovered"
    })

    if recovered:
        # Remove skipped line from notes
        skipped_line = f"- ❓ Unknown format skipped: {path}\n"
        notes = notes.replace(skipped_line, "")
        print(f"✅ Recovered: {path}")
    else:
        print(f"⚠️ Not recovered: {path}")

# Update notes field after sweep
collection.update_one({"_id": cluster_id}, {"$set": {"notes": notes}})
print("\n🧹 Sweep complete. Notes field updated.")
