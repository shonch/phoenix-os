# recover_missing_fragments.py — Final recovery for missed entries
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Final missing paths
MISSING_PATHS = [
    "../../emotional_logs/ache_architect.md",
    "/Users/shonheersink/frisson_journal/outreach/2025-09-02-Upwork Profile.md"
]

# Recover
for path in MISSING_PATHS:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        fragment = {
            "fragment": "recovered",
            "source_path": os.path.abspath(path),
            "filename": os.path.basename(path),
            "content": content,
            "inserted_at": datetime.now().isoformat()
        }
        collection.insert_one(fragment)
        print(f"✅ Recovered: {fragment['filename']}")
    except Exception as e:
        print(f"⚠️ Failed to recover {path}: {e}")
