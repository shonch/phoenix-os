# scan_skipped_echoes.py — Field Visibility Ritual
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

# Fields to scan
fields = ["message", "notes", "content", "log", "recovery_notes"]
pattern = "❓ Unknown format skipped:"

print("\n🔍 Scanning for skipped echoes...\n")

count = 0
for doc in collection.find({}):
    for field in fields:
        value = doc.get(field, "")
        if isinstance(value, str) and any(line.startswith(pattern) for line in value.splitlines()):
            print(f"👁️ Skipped echo found in fragment {str(doc['_id'])[:6]} → field: {field}")
            count += 1
            break  # Only report once per document

print(f"\n✅ Scan complete. {count} fragments contain skipped echoes.")
