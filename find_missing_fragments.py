import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env from phoenix_portfolio
load_dotenv(dotenv_path=".env")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["fragments"]

# Step 1: Get all .md and .txt files in phoenix/
phoenix_dir = "../"
local_files = [
    f for f in os.listdir(phoenix_dir)
    if f.endswith(".md") or f.endswith(".txt")
]

# Step 2: Get all filenames from MongoDB
db_filenames = collection.distinct("filename")
db_filenames_clean = [f.strip() for f in db_filenames if f]

# Step 3: Compare and find missing files
missing_files = [f for f in local_files if f not in db_filenames_clean]

print("📁 Files in phoenix/ not found in MongoDB:")
for f in missing_files:
    print("-", f)

print(f"\nTotal missing: {len(missing_files)}")
