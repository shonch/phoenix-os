import re
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load Valhalla environment variables
load_dotenv(dotenv_path="/Users/shonheersink/git_repos/active/emotional_budget_tracker/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["tag_index"]

# Path to tag_index.txt
TAG_INDEX_PATH = "rituals/tag_index.txt"

# Regex pattern to extract fields
pattern = re.compile(
    r"^(.*?)\: General '(.*?)' → (.*?) \| Tags: (.*)$"
)

def parse_line(line):
    match = pattern.match(line.strip())
    if not match:
        return None

    raw_timestamp, title, path, tags_str = match.groups()
    try:
        timestamp = datetime.strptime(raw_timestamp.strip(), "%a %b %d %H:%M:%S %Z %Y")
    except Exception:
        timestamp = raw_timestamp.strip()  # fallback to raw string

    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    return {
        "timestamp": timestamp,
        "title": title,
        "path": path,
        "tags": tags
    }

def migrate_tag_index():
    with open(TAG_INDEX_PATH, "r") as file:
        for line in file:
            entry = parse_line(line)
            if entry:
                collection.insert_one(entry)
                print(f"🪶 Migrated: {entry['title']}")

if __name__ == "__main__":
    migrate_tag_index()
    print(f"✅ Tag index migration complete to {DB_NAME}/tag_index.")
