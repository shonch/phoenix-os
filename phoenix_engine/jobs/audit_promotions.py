# phoenix_engine/jobs/audit_promotions.py

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

tag_index = db["tag_index"]
promotion_log = db["promotion_log"]

def audit_promotions(limit=20):
    """
    Prints out the most recent promoted tags and their scores.
    """
    print(f"\n=== Audit Report ({datetime.utcnow().isoformat()}) ===")

    # Show promoted tags from tag_index
    promoted_tags = tag_index.find({"promotion_status": "promoted"}).sort("last_promoted_at", -1).limit(limit)
    print("\n-- Promoted Tags (tag_index) --")
    for tag in promoted_tags:
        print(f"{tag.get('tag_name')} | Score: {tag.get('promotion_score')} | Promoted At: {tag.get('last_promoted_at')}")

    # Show recent promotion logs
    logs = promotion_log.find({}).sort("timestamp", -1).limit(limit)
    print("\n-- Promotion Log Entries --")
    for log in logs:
        print(f"{log.get('tag_name')} | Status: {log.get('promotion_status')} | Score: {log.get('promotion_score')} | Timestamp: {log.get('timestamp')}")

if __name__ == "__main__":
    audit_promotions()
