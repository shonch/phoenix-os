from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load env
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Path to check
path = "/Users/shonheersink/Phoenix/emotional_logs/ache_architect.md"

# Query
doc = collection.find_one({"source_path": path})
if doc:
    print("✅ Fragment FOUND in MongoDB.")
    print(f"Status: {doc.get('status')}, Fragment: {doc.get('fragment')}")
else:
    print("❌ Fragment NOT found in MongoDB.")
