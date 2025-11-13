# backend/modules/normalize_tags.py
# TEMPORARY: Normalize all tag_name fields in symbolic_tags
# Marked for deletion after Phoenix iOS migration

from backend.mongo_client import db
from backend.modules.symbolic_tag import normalize_tag

def run():
    count = 0
    for doc in db["symbolic_tags"].find():
        normalized = normalize_tag(doc["tag_name"])
        if normalized != doc["tag_name"]:
            db["symbolic_tags"].update_one(
                {"_id": doc["_id"]},
                {"$set": {"tag_name": normalized}}
            )
            count += 1
    print(f"🔧 Normalized {count} tag names in symbolic_tags.")

if __name__ == "__main__":
    run()
