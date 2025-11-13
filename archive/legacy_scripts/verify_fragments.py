from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env from current directory
load_dotenv(dotenv_path=".env")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

# Choose the collection that holds .md and .txt fragments
collection = db["fragments"]

# List all filenames
docs = collection.find({}, {"filename": 1, "_id": 0})
print("Files stored in 'fragments':")
for doc in docs:
    print(doc.get("filename"))
