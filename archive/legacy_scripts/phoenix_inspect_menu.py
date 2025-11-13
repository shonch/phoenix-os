from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pprint

load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
client = MongoClient(os.getenv("MONGO_URI"))
db = client["backend"]

# Search all collections for the path
target = "/Users/shonheersink/Phoenix/README.md"
collections = db.list_collection_names()

for name in collections:
    collection = db[name]
    doc = collection.find_one({"notes": {"$regex": target}})
    if doc:
        print(f"\n📄 Found in collection: {name}")
        pprint.pprint(doc)
