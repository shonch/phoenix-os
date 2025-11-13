# tag_audit_oneoff.py — One-Time Phoenix Tag Inspection
# Author: Shon Heersink & Copilot

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env from phoenix_portfolio
load_dotenv(dotenv_path=".env")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

def audit_tags():
    tag_index = db["tag_index"]
    symbolic_tags = db["symbolic_tags"]

    untitled_index = tag_index.count_documents({ "title": { "$exists": False } })
    untitled_symbolic = symbolic_tags.count_documents({ "title": { "$exists": False } })

    print("\n🧭 Phoenix Tag Audit — One-Time Inspection")
    print(f"🔍 Untitled in tag_index: {untitled_index}")
    print(f"🔍 Untitled in symbolic_tags: {untitled_symbolic}")

    print("\n📦 Sample tag_index records:")
    for doc in tag_index.find().limit(5):
        print(doc)

    print("\n📦 Sample symbolic_tags records:")
    for doc in symbolic_tags.find().limit(5):
        print(doc)

    print("\n🕊️ Audit complete. You may now return to Phoenix console.")

if __name__ == "__main__":
    audit_tags()
