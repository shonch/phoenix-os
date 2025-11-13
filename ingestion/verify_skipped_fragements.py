# verify_skipped_fragments.py — Confirm all skipped fragments are in MongoDB
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Load skipped paths
with open("../../skipped_paths.txt", "r") as f:
    paths = [line.strip() for line in f.readlines() if line.strip()]

# Check each path
missing = []
for path in paths:
    if not collection.find_one({"source_path": path}):
        missing.append(path)

# Report
if missing:
    print("⚠️ Missing fragments:")
    for m in missing:
        print(f"- {m}")
else:
    print("✅ All skipped fragments are present in MongoDB.")
