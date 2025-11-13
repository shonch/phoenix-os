from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

collection = db["fragments"]

# Find one document where filename is missing
doc = collection.find_one({"filename": None})

if doc:
    print("Document with missing filename:")
    print(doc)
else:
    print("No documents with missing filename found.")
