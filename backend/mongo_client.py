# mongo_client.py — Phoenix Cloud Connector
# Author: Shon Heersink & Copilot

import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv

# 🌐 Load .env file from any launch context
load_dotenv(find_dotenv())

# 🔐 Retrieve credentials from environment
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# 🧠 Connect to Phoenix cloud database
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 🩺 Connection check — list collections
try:
    print("Phoenix connection established:", db.list_collection_names())
except Exception as e:
    print("⚠️ Phoenix connection failed:", e)
