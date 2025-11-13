# inspect_collections_dual.py — Ritual Inspection of Phoenix and Valhalla Collections

import os
from pymongo import MongoClient
from dotenv import dotenv_values

def load_env(path):
    env_vars = dotenv_values(path)
    return env_vars.get("MONGO_URI"), env_vars.get("DB_NAME")

def inspect(uri, db_name, label):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print(f"\n📂 {label} — Collections in '{db_name}':")
        for name in db.list_collection_names():
            print(f" - {name}")
    except Exception as e:
        print(f"⚠️ Error inspecting {label}: {e}")

def run():
    # Phoenix — .env is in current directory
    phoenix_env = os.path.abspath(".env")
    phoenix_uri, phoenix_db = load_env(phoenix_env)
    if not phoenix_uri or not phoenix_db:
        print("⚠️ Phoenix .env not loaded correctly.")
        print(f"MONGO_URI: {phoenix_uri}")
        print(f"DB_NAME: {phoenix_db}")
    else:
        inspect(phoenix_uri, phoenix_db, "Phoenix")

    # Valhalla — use corrected absolute path
    valhalla_env = "/Users/shonheersink/git_repos/active/emotional_budget_tracker/.env"
    valhalla_uri, valhalla_db = load_env(valhalla_env)
    if not valhalla_uri or not valhalla_db:
        print("⚠️ Valhalla .env not loaded correctly.")
        print(f"MONGO_URI: {valhalla_uri}")
        print(f"DB_NAME: {valhalla_db}")
    else:
        inspect(valhalla_uri, valhalla_db, "Valhalla")

if __name__ == "__main__":
    run()
