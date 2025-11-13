# purge_skipped_from_message.py — Final Ghost Sweep (Verified)
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Confirm environment loading
print("🔌 Connecting to MongoDB...")
print("MONGO_URI:", MONGO_URI)
print("DB_NAME:", DB_NAME)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Sweep and purge
docs = collection.find({})
count = 0

for doc in docs:
    message = doc.get("message", "")
    lines = message.splitlines()
    cleaned_lines = [line for line in lines if not line.startswith("❓ Unknown format skipped:")]
    new_message = "\n".join(cleaned_lines)

    if new_message != message:
        collection.update_one({"_id": doc["_id"]}, {"$set": {"message": new_message}})
        print(f"🧹 Purged skipped echoes from message in fragment {str(doc['_id'])[:6]}")
        count += 1

print(f"\n✅ Purged {count} fragments. Skipped echoes removed from message fields. Phoenix is clean.")
