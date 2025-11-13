# sync_tags.py — Sync symbolic_tags into tag_index for Phoenix suggestions

from backend.mongo_client import db
from backend.modules.symbolic_tag import normalize_tag

def sync_tags():
    symbolic_tags = db["symbolic_tags"].find()
    existing_tags = set(t["tag_name"] for t in db["tag_index"].find())

    new_entries = []
    for tag in symbolic_tags:
        normalized = normalize_tag(tag["tag_name"])
        if normalized not in existing_tags:
            new_entries.append({
                "tag_name": normalized,
                "usage_count": tag.get("usage_count", 1)
            })

    if new_entries:
        db["tag_index"].insert_many(new_entries)
        print(f"🌱 Synced {len(new_entries)} new tags into tag_index.")
    else:
        print("✅ tag_index already contains all symbolic tags.")

if __name__ == "__main__":
    sync_tags()
