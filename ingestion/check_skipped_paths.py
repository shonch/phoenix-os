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

# List of skipped paths to check
SKIPPED_PATHS = [
    "/Users/shonheersink/Phoenix/emotional_logs/ache_architect.md",
    "/Users/shonheersink/frisson_journal/outreach/2025-09-02-Upwork Profile.md",
    # Add more paths here if needed
]

for path in SKIPPED_PATHS:
    result = collection.find_one({"source_path": path})
    if result:
        print(f"✅ Found in MongoDB: {path}")
    else:
        print(f"❌ Missing from MongoDB: {path}")
