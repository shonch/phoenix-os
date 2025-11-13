# inspect_valhalla_documents.py — Peek into Valhalla's setup_items and transactions

import os
from pymongo import MongoClient
from dotenv import dotenv_values
from pprint import pprint

# Load Valhalla .env
valhalla_env = "/Users/shonheersink/git_repos/active/emotional_budget_tracker/.env"
env_vars = dotenv_values(valhalla_env)
uri = env_vars.get("MONGO_URI")
db_name = env_vars.get("DB_NAME")

client = MongoClient(uri)
db = client[db_name]

# Inspect setup_items
print("\n🔍 setup_items sample document:")
setup_sample = db["setup_items"].find_one()
pprint(setup_sample)

# Inspect transactions
print("\n🔍 transactions sample document:")
transaction_sample = db["transactions"].find_one()
pprint(transaction_sample)
