import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from core import scan_manifest

# Load PhoenixOS environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Load fragments from manifest
manifest_path = "../../md_manifest.txt"
fragments = scan_manifest(manifest_path)

# Insert fragments with duplicate check
inserted_count = 0
skipped_count = 0

for frag in fragments:
    if not collection.find_one({"source_path": frag.get("source_path")}):
        frag["inserted_at"] = datetime.now().isoformat()
        collection.insert_one(frag)
        inserted_count += 1
    else:
        print(f"⏸️ Skipped duplicate: {frag.get('source_path')}")
        skipped_count += 1

print(f"✅ Inserted {inserted_count} new fragments into {DB_NAME}/fragments")
print(f"⏸️ Skipped {skipped_count} duplicates")
