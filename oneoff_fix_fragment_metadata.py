# oneoff_fix_fragment_metadata.py — Phoenix Metadata Recovery Ritual
# Author: Shon Heersink & Copilot

import re
from backend.mongo_client import db

def extract_metadata(content):
    title_match = re.search(r"\*\*Title\*\*:\s*(.+)", content)
    emotion_match = re.search(r"\*\*Emotion\*\*:\s*(.+)", content)
    logged_match = re.search(r"\*\*Logged\*\*:\s*(.+)", content)

    title = title_match.group(1).strip() if title_match else None
    emotion = emotion_match.group(1).strip() if emotion_match else None
    logged = logged_match.group(1).strip() if logged_match else None

    return title, emotion, logged

def run():
    collection = db["emotional_fragments"]
    cursor = collection.find({})

    updated = 0
    skipped = 0

    for doc in cursor:
        content = doc.get("content", "")
        title, emotion, logged = extract_metadata(content)

        updates = {}
        if title and not doc.get("title"):
            updates["title"] = title
        if emotion and not doc.get("emotion"):
            updates["emotion"] = emotion
        if logged and not doc.get("logged"):
            updates["logged"] = logged

        if updates:
            collection.update_one({"_id": doc["_id"]}, {"$set": updates})
            updated += 1
        else:
            skipped += 1

    print(f"✅ Metadata recovery complete — {updated} fragments updated, {skipped} skipped.")

if __name__ == "__main__":
    run()
