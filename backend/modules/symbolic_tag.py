# phoenix_portfolio/backend/modules/symbolic_tag.py

from datetime import datetime
import os

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

from phoenix_portfolio.phoenix_engine.models.tag import PhoenixTag


# -----------------------------
# Normalization Helpers
# -----------------------------

def normalize_label(name: str) -> str:
    """
    Normalize a raw tag name into a canonical, lowercase, underscore form.
    """
    if not isinstance(name, str):
        return ""
    return (
        name.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _normalize_legacy_fields(tag: dict) -> dict:
    """
    Clean legacy Phoenix tags so they conform to the PhoenixTag schema.
    Prevents ingestion failures when old tags contain invalid values.
    """

    # emotional_weight must be float or None
    ew = tag.get("emotional_weight")
    if isinstance(ew, str):
        if ew.lower() in ["neutral", "none", "zero", ""]:
            tag["emotional_weight"] = None
        else:
            try:
                tag["emotional_weight"] = float(ew)
            except Exception:
                tag["emotional_weight"] = None

    # visibility must be a string
    if tag.get("visibility") is None:
        tag["visibility"] = "private"

    # archetype must be a string
    if tag.get("archetype") is None:
        tag["archetype"] = "emergent"

    # category must be a string
    if tag.get("category") is None:
        tag["category"] = "custom"

    # emoji must be a string
    if tag.get("emoji") is None:
        tag["emoji"] = "🌀"

    # description must be a string
    if tag.get("description") is None:
        tag["description"] = ""

    return tag


# -----------------------------
# Mongo Setup
# -----------------------------

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "phoenix_engine")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["symbolic_tags"]


# -----------------------------
# Core Tag Engine
# -----------------------------

def normalize_tag(tag_data: dict) -> dict:
    """
    Normalize a single tag object into a canonical PhoenixTag-shaped dict.

    Behavior:
      - Accepts full tag objects (not strings)
      - If tag_id exists → resolve existing tag
      - If no tag_id → create/update via create_tag()
      - Always returns a PhoenixTag-compatible dict
    """

    if not isinstance(tag_data, dict):
        return {}

    # 1. Extract name + normalize label
    raw_name = tag_data.get("name") or tag_data.get("label") or ""
    if not raw_name:
        return {}

    label = normalize_label(raw_name)
    user_id = tag_data.get("user_id")

    # 2. If tag_id exists → resolve
    tag_id = tag_data.get("tag_id")
    if tag_id:
        existing = None

        # Try resolving by Mongo _id
        try:
            oid = ObjectId(tag_id)
            existing = collection.find_one({"_id": oid})
        except Exception:
            existing = None

        # Fallback: resolve by label + user_id
        if not existing and user_id:
            existing = collection.find_one({"label": label, "user_id": user_id})

        if existing:
            existing = _normalize_legacy_fields(existing)
            existing["_id"] = str(existing["_id"])
            existing["tag_id"] = existing.get("tag_id", existing["_id"])
            return existing

    # 3. No tag_id → create/update
    create_payload = {
        "name": raw_name,
        "user_id": user_id,
        "emoji": tag_data.get("emoji"),
        "category": tag_data.get("category"),
        "description": tag_data.get("description"),
        "archetype": tag_data.get("archetype"),
        "visibility": tag_data.get("visibility"),
        "color": tag_data.get("color"),
        "emotional_weight": tag_data.get("emotional_weight"),
        "sass_level": tag_data.get("sass_level"),
        "dominatrix_affinity": tag_data.get("dominatrix_affinity"),
        "source_system": tag_data.get("source_system"),
    }

    created = create_tag(create_payload)
    created["tag_id"] = created.get("tag_id", str(created.get("_id", "")))
    return created


def suggest_tags(partial: str, limit: int = 5) -> list:
    """
    Suggest symbolic tags based on partial input.
    Matches substrings against the 'label' field and returns
    the most frequently used tags (times_used desc).
    """
    partial = normalize_label(partial)
    matches = collection.find(
        {"label": {"$regex": partial, "$options": "i"}}
    ).sort("times_used", -1)

    return list(matches.limit(limit))


def create_tag(tag_data: dict) -> dict:
    """
    Create or update a symbolic tag using the unified PhoenixTag schema.
    """

    if "name" not in tag_data:
        raise ValueError("tag_data must include 'name'")

    if "user_id" not in tag_data:
        raise ValueError("tag_data must include 'user_id'")

    raw_name = tag_data["name"]
    user_id = tag_data["user_id"]
    label = normalize_label(raw_name)

    # Check for existing tag
    existing = collection.find_one({"label": label, "user_id": user_id})

    if existing:
        # Update existing tag
        existing["times_used"] = existing.get("times_used", 1) + 1
        existing["updated_at"] = datetime.utcnow().isoformat()

        # Apply new fields
        for key, value in tag_data.items():
            if value is not None:
                existing[key] = value

        # Normalize legacy fields
        existing = _normalize_legacy_fields(existing)

        collection.update_one({"_id": existing["_id"]}, {"$set": existing})
        return existing

    # Create new PhoenixTag
    tag = PhoenixTag(
        name=raw_name,
        label=label,
        user_id=user_id,
        emoji=tag_data.get("emoji", "🌀"),
        category=tag_data.get("category", "custom"),
        description=tag_data.get("description", ""),
        archetype=tag_data.get("archetype", "emergent"),
        visibility=tag_data.get("visibility", "private"),
        color=tag_data.get("color"),
        emotional_weight=tag_data.get("emotional_weight"),
        sass_level=tag_data.get("sass_level"),
        dominatrix_affinity=tag_data.get("dominatrix_affinity"),
        source_system=tag_data.get("source_system"),
        user_ids=[user_id],
    )

    tag_dict = tag.dict()

    # Normalize before saving
    tag_dict = _normalize_legacy_fields(tag_dict)

    result = collection.insert_one(tag_dict)
    tag_dict["_id"] = str(result.inserted_id)

    return tag_dict


def select_tag(query: dict) -> list:
    """
    Retrieves symbolic tags matching a Mongo-style query.
    """
    return list(collection.find(query))


def list_tags(user_id: str | None = None) -> list:
    """
    Returns symbolic tags.
    """
    query = {"user_id": user_id} if user_id else {}
    return list(collection.find(query))


def render_overlay(tag_id: str) -> dict:
    """
    Returns expressive overlay logic for CLI or UI rendering.
    """
    try:
        oid = ObjectId(tag_id)
    except Exception:
        return {}

    tag = collection.find_one({"_id": oid})
    if not tag:
        return {}

    tag = _normalize_legacy_fields(tag)

    return {
        "emoji": tag.get("emoji", "🌀"),
        "color": tag.get("color", "#999999"),
        "archetype": tag.get("archetype", "unknown"),
        "emotional_weight": tag.get("emotional_weight", None),
        "label": tag.get("label", "unnamed_tag"),
        "name": tag.get("name", tag.get("label", "")),
    }


def update_tag(tag_id: str, updates: dict) -> bool:
    """
    Updates a symbolic tag with new values.
    """
    try:
        oid = ObjectId(tag_id)
    except Exception:
        return False

    updates["updated_at"] = datetime.utcnow().isoformat()

    # Normalize legacy fields before saving
    updates = _normalize_legacy_fields(updates)

    result = collection.update_one({"_id": oid}, {"$set": updates})
    return result.modified_count > 0

