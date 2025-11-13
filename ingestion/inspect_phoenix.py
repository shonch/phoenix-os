from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load PhoenixOS environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"📦 Collections in {DB_NAME}:")
collections = db.list_collection_names()
if not collections:
    print("⚠️ No collections found. Check DB_NAME or connection.")
else:
    for name in collections:
        count = db[name].count_documents({})
        print(f" - {name} ({count} docs)")

    print("\n🔍 Sample documents from each collection:")
    for name in collections:
        print(f"\n🗂️ {name}:")
        docs = db[name].find().limit(2)
        found = False
        for doc in docs:
            print(doc)
            found = True
        if not found:
            print("⚠️ No documents found.")
