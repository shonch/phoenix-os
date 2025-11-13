from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Input and output files
input_file = "skipped_paths.txt"
output_file = "skipped_paths_remaining.txt"

with open(input_file, "r") as f:
    paths = [line.strip() for line in f if line.strip()]

remaining = []

for path in paths:
    path = os.path.abspath(path)
    doc = collection.find_one({"source_path": path})
    if doc:
        print(f"✅ Recovered: {path}")
    else:
        print(f"❌ Still missing: {path}")
        remaining.append(path)

# Write cleaned list
with open(output_file, "w") as f:
    for path in remaining:
        f.write(path + "\n")

print(f"\n🧹 Cleaned log written to {output_file}")
