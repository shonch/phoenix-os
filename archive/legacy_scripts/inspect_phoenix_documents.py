# inspect_phoenix_documents.py — Ritual Glimpse into Phoenix Fragments

import os
from pymongo import MongoClient
from dotenv import dotenv_values
from pprint import pprint

# Load Phoenix .env
phoenix_env = os.path.abspath(".env")
env_vars = dotenv_values(phoenix_env)
uri = env_vars.get("MONGO_URI")
db_name = env_vars.get("DB_NAME")

client = MongoClient(uri)
db = client[db_name]

collections = ["emotional_fragments", "clues", "revelations", "fragments", "tag_index"]

for name in collections:
    print(f"\n🔍 {name} sample document:")
    doc = db[name].find_one()
    pprint(doc)
