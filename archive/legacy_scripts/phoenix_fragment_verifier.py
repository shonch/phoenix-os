# phoenix_fragment_verifier.py — Single Fragment Truth Sweep
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pprint

# 🔐 Load environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# 🔍 Step 1: Choose the skipped path to verify
target_path = "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-31-evening-release.md"

# 🔍 Step 2: Find original fragment with the skipped note
original = collection.find_one({
    "notes": {"$regex": f"Unknown format skipped: {target_path}"}
})

print("\n📄 Original Fragment:")
if original:
    pprint.pprint(original)
else:
    print("❌ No original fragment found with skipped note.")

# 🔍 Step 3: Check for recovered fragment
recovered = collection.find_one({
    "source_path": target_path,
    "fragment": "recovered"
})

print("\n🛡️ Recovered Fragment:")
if recovered:
    pprint.pprint(recovered)
else:
    print("⚠️ No recovered fragment found for this path.")
