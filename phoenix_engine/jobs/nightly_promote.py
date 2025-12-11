# phoenix_engine/jobs/nightly_promote.py

from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Import utilities
from phoenix_engine.utils.tag_utils import promote_tag

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

symbolic_tags = db["symbolic_tags"]
tag_index = db["tag_index"]
promotion_log = db["promotion_log"]

def run_nightly_promotion():
    """
    Iterates through all symbolic_tags, calculates scores,
    promotes qualifying tags into tag_index, and logs actions.
    """
    tags = symbolic_tags.find({})
    promoted_count = 0

    for tag in tags:
        promoted_doc = promote_tag(tag, tag_index, promotion_log)
        if promoted_doc["promotion_status"] == "promoted":
            promoted_count += 1

    print(f"[{datetime.utcnow().isoformat()}] Nightly promotion complete.")
    print(f"Tags promoted: {promoted_count}")

if __name__ == "__main__":
    run_nightly_promotion()
