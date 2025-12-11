# backend/modules/symbolic_tag.py

from pymongo import MongoClient
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
from phoenix_engine.utils.tag_utils import calculate_score

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to Phoenix DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["symbolic_tags"]

def suggest_tags(partial: str, limit: int = 5) -> list:
    """
    Suggests symbolic tags based on partial input.
    Matches substrings and returns most frequently used tags.
    """
    partial = normalize_tag(partial)
    matches = collection.find({"tag_name": {"$regex": partial, "$options": "i"}})
    sorted_matches = sorted(matches, key=lambda x: x.get("usage_count", 0), reverse=True)
    return sorted_matches[:limit]

def create_tag(tag_data: dict) -> str:
    tag_name = normalize_tag(tag_data["tag_name"])
    existing = collection.find_one({"tag_name": tag_name})

    if existing:
        # Update usage count
        new_count = existing.get("usage_count", 1) + 1
        updates = {"usage_count": new_count}

        # Enrich missing fields
        for field in ["title", "emoji", "archetype", "description", "color", "emotional_weight"]:
            if field not in existing and field in tag_data:
                updates[field] = tag_data[field]

        # Add user_id if provided
        if "user_id" in tag_data:
            user_ids = existing.get("user_ids", [])
            if tag_data["user_id"] not in user_ids:
                user_ids.append(tag_data["user_id"])
            updates["user_ids"] = user_ids

        # Recalculate promotion score
        score = calculate_score({**existing, **updates})
        updates["promotion_score"] = score
        updates["promotion_status"] = "candidate" if score < 0.7 else "promoted"
        if score >= 0.7:
            updates["last_promoted_at"] = datetime.utcnow().isoformat()

        collection.update_one({"tag_name": tag_name}, {"$set": updates})
        return existing["tag_id"]

    else:
        # Create new tag
        tag_data["tag_name"] = tag_name
        tag_data["tag_id"] = str(uuid.uuid4())
        tag_data["created_at"] = datetime.utcnow().isoformat()
        tag_data["usage_count"] = 1

        # Initialize promotion fields
        tag_data["user_ids"] = [tag_data.get("user_id")] if "user_id" in tag_data else []
        tag_data["promotion_score"] = calculate_score(tag_data)
        tag_data["promotion_status"] = "candidate"
        tag_data["last_promoted_at"] = None
        tag_data["version"] = 1

        collection.insert_one(tag_data)
        return tag_data["tag_id"]
def select_tag(query: dict) -> list:
    """
    Retrieves symbolic tags matching a query.
    Example: {"archetype": "guardian", "sass_level": {"$gte": 5}}
    """
    return list(collection.find(query))

def list_tags() -> list:
    """
    Returns all symbolic tags in the collection.
    """
    return list(collection.find())

def normalize_tag(tag: str) -> str:
    return tag.strip().lower().replace("-", "_").replace(" ", "_")

def render_overlay(tag_id: str) -> dict:
    """
    Returns expressive overlay logic for CLI or UI rendering.
    Includes color, sass level, archetype, and emotional weight.
    """
    tag = collection.find_one({"tag_id": tag_id})
    if not tag:
        return {}

    return {
        "emoji": tag.get("emoji", "🌀"),
        "color": tag.get("color", "#999999"),
        "sass_level": tag.get("sass_level", 0),
        "archetype": tag.get("archetype", "unknown"),
        "emotional_weight": tag.get("emotional_weight", "neutral"),
        "label": tag.get("tag_name", "Unnamed Tag"),
        "dominatrix_affinity": tag.get("dominatrix_affinity", [])
    }

def update_tag(tag_id: str, updates: dict) -> bool:
    """
    Updates a symbolic tag with new values.
    """
    result = collection.update_one({"tag_id": tag_id}, {"$set": updates})
    return result.modified_count > 0
