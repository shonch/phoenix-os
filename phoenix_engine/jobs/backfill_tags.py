# phoenix_engine/jobs/backfill_tags.py

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Import scoring utility
from phoenix_engine.utils.tag_utils import calculate_score

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

symbolic_tags = db["symbolic_tags"]

def backfill_tags():
    """
    Adds missing promotion fields to existing symbolic_tags documents.
    Ensures every tag has user_ids, promotion_score, promotion_status, last_promoted_at, and version.
    """
    tags = symbolic_tags.find({})
    updated_count = 0

    for tag in tags:
        updates = {}

        # Ensure user_ids field exists
        if "user_ids" not in tag:
            updates["user_ids"] = []

        # Ensure version field exists
        if "version" not in tag:
            updates["version"] = 1

        # Calculate promotion score
        score = calculate_score({**tag, **updates})
        updates["promotion_score"] = score

        # Set promotion status
        if score >= 0.7:
            updates["promotion_status"] = "promoted"
            updates["last_promoted_at"] = datetime.utcnow().isoformat()
        else:
            updates["promotion_status"] = "candidate"
            updates["last_promoted_at"] = None

        if updates:
            symbolic_tags.update_one({"_id": tag["_id"]}, {"$set": updates})
            updated_count += 1

    print(f"Backfill complete. Updated {updated_count} tags.")

if __name__ == "__main__":
    backfill_tags()
