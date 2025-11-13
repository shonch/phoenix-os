from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Load skipped paths
with open("skipped_paths.txt", "r") as f:
    paths = [line.strip() for line in f if line.strip()]

print(f"\n🔍 Starting recovery sweep for {len(paths)} paths...\n")

for path in paths:
    # Normalize path
    path = os.path.abspath(path)

    # Check if already recovered
    if collection.find_one({"source_path": path, "fragment": "recovered"}):
        print(f"🛡️ Already recovered: {path}")
        continue

    # Try to read and insert
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        fragment = {
            "fragment": "recovered",
            "source_path": path,
            "filename": os.path.basename(path),
            "content": content,
            "inserted_at": datetime.now().isoformat()
        }

        collection.insert_one(fragment)
        print(f"✅ Recovered: {path}")

    except Exception as e:
        print(f"❌ Failed to recover: {path}\n   Reason: {e}")
