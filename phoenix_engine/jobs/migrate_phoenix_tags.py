# phoenix_engine/jobs/migrate_phoenix_tags.py

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

from phoenix_engine.models.tag import PhoenixTag

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "phoenix_engine")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["symbolic_tags"]


def normalize_label(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def migrate_tags():
    tags = list(collection.find({}))
    updated_count = 0

    for tag in tags:
        updates = {}

        # -------------------------------
        # 1. Ensure raw name exists
        # -------------------------------
        if "name" not in tag:
            raw_name = (
                tag.get("label") or
                tag.get("tag_name") or
                f"unnamed_tag_{tag['_id']}"
            )
            updates["name"] = raw_name

        # -------------------------------
        # 2. Ensure normalized label exists
        # -------------------------------
        if "label" not in tag:
            raw_name_source = (
                updates.get("name") or
                tag.get("name") or
                tag.get("tag_name") or
                f"unnamed_tag_{tag['_id']}"
            )
            updates["label"] = normalize_label(raw_name_source)

        # -------------------------------
        # 3. Ensure mythic fields exist
        # -------------------------------
        mythic_defaults = {
            "emoji": "🌀",
            "category": "custom",
            "description": "",
            "archetype": "emergent",
            "visibility": "private",
            "color": None,
            "emotional_weight": None,
            "sass_level": None,
            "dominatrix_affinity": None,
        }

        for field, default in mythic_defaults.items():
            if field not in tag:
                updates[field] = default

        # -------------------------------
        # 4. Promotion layer defaults
        # -------------------------------
        promotion_defaults = {
            "source_system": None,
            "times_used": tag.get("times_used", 1),
            "promoted": tag.get("promoted", False),
            "user_ids": (
                [tag.get("user_id")]
                if "user_ids" not in tag
                else tag["user_ids"]
            ),
            "promotion_score": tag.get("promotion_score"),
            "promotion_status": tag.get("promotion_status"),
            "last_promoted_at": tag.get("last_promoted_at"),
            "version": tag.get("version", 1),
        }

        for field, default in promotion_defaults.items():
            if field not in tag:
                updates[field] = default

        # -------------------------------
        # 5. System metadata
        # -------------------------------
        if "created_at" not in tag:
            updates["created_at"] = datetime.utcnow().isoformat()

        updates["updated_at"] = datetime.utcnow().isoformat()

        # -------------------------------
        # 6. Apply updates
        # -------------------------------
        if updates:
            collection.update_one({"_id": tag["_id"]}, {"$set": updates})
            updated_count += 1

    print(f"PhoenixTag migration complete. Updated {updated_count} tags.")


if __name__ == "__main__":
    migrate_tags()

