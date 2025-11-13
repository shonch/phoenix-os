from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load Valhalla environment variables
load_dotenv(dotenv_path="/Users/shonheersink/git_repos/active/emotional_budget_tracker/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"📦 Collections in {DB_NAME}:")
for name in db.list_collection_names():
    print(f" - {name}")

print("\n🔍 Sample documents from each collection:")
for name in db.list_collection_names():
    print(f"\n🗂️ {name}:")
    for doc in db[name].find().limit(2):
        print(doc)
