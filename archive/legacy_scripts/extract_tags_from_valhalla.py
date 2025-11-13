# extract_tags_from_valhalla.py — Migrate symbolic tags from Valhalla to Phoenix

import os
from pymongo import MongoClient
from dotenv import dotenv_values

# Load Valhalla .env
valhalla_env = "/Users/shonheersink/git_repos/active/emotional_budget_tracker/.env"
valhalla_vars = dotenv_values(valhalla_env)
valhalla_uri = valhalla_vars.get("MONGO_URI")
valhalla_db_name = valhalla_vars.get("DB_NAME")

# Load Phoenix .env
phoenix_env = os.path.abspath(".env")
phoenix_vars = dotenv_values(phoenix_env)
phoenix_uri = phoenix_vars.get("MONGO_URI")
phoenix_db_name = phoenix_vars.get("DB_NAME")

# Connect to both databases
valhalla_client = MongoClient(valhalla_uri)
valhalla_db = valhalla_client[valhalla_db_name]

phoenix_client = MongoClient(phoenix_uri)
phoenix_db = phoenix_client[phoenix_db_name]
tag_index = phoenix_db["tag_index"]

def insert_tag(label, source, doc_id, context, user_id=None):
    if not label:
        return
    tag_doc = {
        "label": label.strip(),
        "type": "symbolic_tag",
        "source_collection": source,
        "document_id": str(doc_id),
        "context": context,
    }
    if user_id:
        tag_doc["user_id"] = user_id
    tag_index.insert_one(tag_doc)
    print(f"✅ Indexed tag: {label} from {source} ({doc_id})")

# Process setup_items
print("\n🔍 Scanning setup_items...")
for doc in valhalla_db["setup_items"].find():
    doc_id = doc["_id"]
    context = doc.get("name", "")
    user_id = doc.get("user_id")

    insert_tag(doc.get("symbolic_tag"), "valhalla.setup_items", doc_id, context, user_id)
    insert_tag(doc.get("symbolic_time"), "valhalla.setup_items", doc_id, context, user_id)
    insert_tag(doc.get("archetype"), "valhalla.setup_items", doc_id, context, user_id)
    insert_tag(doc.get("emotion_tag_id"), "valhalla.setup_items", doc_id, context, user_id)

# Process transactions
print("\n🔍 Scanning transactions...")
for doc in valhalla_db["transactions"].find():
    doc_id = doc["_id"]
    context = doc.get("description", "")
    user_id = doc.get("user_id")

    insert_tag(doc.get("tags"), "valhalla.transactions", doc_id, context, user_id)
    insert_tag(doc.get("emotional_weight"), "valhalla.transactions", doc_id, context, user_id)
