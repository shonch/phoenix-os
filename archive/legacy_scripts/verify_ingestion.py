from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("MONGO_URI:", os.getenv("MONGO_URI"))
# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["backend"]

print("Collections in backend:")
print(db.list_collection_names())
