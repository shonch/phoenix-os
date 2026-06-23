# phoenix_portfolio/backend/persistence/fragments.py

from bson import ObjectId
import datetime

from ...phoenix_engine.utils.mongo_client import db
from ..modules import symbolic_tag
from ..schemas.api_fragments import Tag


# -----------------------------
# Tag Resolution
# -----------------------------

def _resolve_tag_id(tag_id: str) -> Tag:
    matches = symbolic_tag.select_tag({"tag_id": tag_id})
    if matches:
        tag_dict = dict(matches[0])
        tag_dict.pop("_id", None)
        return Tag(**tag_dict)

    return Tag(
        tag_id=tag_id,
        name="legacy",
        label="legacy",
        emoji="🌀",
        category="legacy",
        description="",
        archetype="legacy",
        visibility="private",
        user_id="system",
    )


# -----------------------------
# Fragment Conversion
# -----------------------------

def _convert_mongo_fragment(doc: dict) -> dict:
    if not doc:
        return None

    # Convert Mongo _id → id
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)

    # Normalize timestamps
    ts = doc.get("timestamp") or doc.get("created_at") or doc.get("date")
    if isinstance(ts, (datetime.datetime, datetime.date)):
        ts = ts.isoformat()
    doc["created_at"] = ts

    # Resolve tag IDs → full Tag objects
    tag_ids = doc.get("tags", [])
    resolved = []
    for tid in tag_ids:
        resolved.append(_resolve_tag_id(tid))

    doc["tags"] = [t.dict() for t in resolved]

    return doc


# -----------------------------
# Insert Fragment (Router-driven)
# -----------------------------

def insert_fragment(fragment_doc: dict) -> str:
    """
    The router (build_fragment_document) sets fragment_doc["collection"].
    We honor that and write to the correct Mongo collection.
    """
    if not isinstance(fragment_doc, dict):
        raise ValueError("fragment_doc must be a dict")

    doc = dict(fragment_doc)
    collection_name = doc.pop("collection", "fragments")

    collection = db[collection_name]
    result = collection.insert_one(doc)
    return str(result.inserted_id)


# -----------------------------
# Read Operations (Router expects these)
# -----------------------------

def get_all_fragments() -> list:
    """
    Return all fragments from ALL fragment collections.
    The router expects a unified view.
    """
    fragments = []

    for name in ["emotional_fragments", "fragments", "raw_documents"]:
        if name in db.list_collection_names():
            for doc in db[name].find().sort("timestamp", -1):
                converted = _convert_mongo_fragment(doc)
                if converted:
                    fragments.append(converted)

    return fragments


def get_fragment_by_id(fragment_id: str) -> dict:
    """
    Search all fragment collections for a matching _id.
    """
    try:
        oid = ObjectId(fragment_id)
    except Exception:
        return None

    for name in ["emotional_fragments", "fragments", "raw_documents"]:
        if name in db.list_collection_names():
            doc = db[name].find_one({"_id": oid})
            if doc:
                return _convert_mongo_fragment(doc)

    return None


def search_fragments(query: str) -> list:
    """
    Simple text search across all fragment collections.
    """
    results = []

    for name in ["emotional_fragments", "fragments", "raw_documents"]:
        if name in db.list_collection_names():
            cursor = db[name].find(
                {"$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"subject": {"$regex": query, "$options": "i"}},
                    {"body": {"$regex": query, "$options": "i"}},
                ]}
            ).sort("timestamp", -1)

            for doc in cursor:
                converted = _convert_mongo_fragment(doc)
                if converted:
                    results.append(converted)

    return results


def get_fragments_by_tag(label: str) -> list:
    """
    Find fragments whose resolved tags include a tag with this label.
    """
    results = []

    # First resolve the tag(s) with this label
    matches = symbolic_tag.select_tag({"label": label})
    tag_ids = [m.get("tag_id") for m in matches if m.get("tag_id")]

    if not tag_ids:
        return []

    for name in ["emotional_fragments", "fragments", "raw_documents"]:
        if name in db.list_collection_names():
            cursor = db[name].find({"tags": {"$in": tag_ids}}).sort("timestamp", -1)
            for doc in cursor:
                converted = _convert_mongo_fragment(doc)
                if converted:
                    results.append(converted)

    return results

