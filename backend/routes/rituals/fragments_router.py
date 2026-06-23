# phoenix_portfolio/backend/routes/rituals/fragments_router.py
# Phoenix Fragments API — Unified Fragment Index

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.schemas.fragments import Fragment

router = APIRouter(tags=["fragments"])

# All collections that hold Phoenix fragments, with a default "type" hint
FRAGMENT_COLLECTIONS = [
    ("fragments", "emotion_fragment"),          # log_emotion.py
    ("emotional_fragments", "emotional_fragment"),  # pulse, grind, anti-grind, mirror, etc.
    ("revelations", "revelation"),
    ("thresholds", "threshold"),
    ("clues", "clue"),
]


def _normalize_doc(doc: dict, collection: str, default_type: Optional[str] = None) -> Fragment:
    """Normalize raw Mongo docs into a unified Fragment model."""
    frag_id = str(doc.get("_id"))

    # Try to find a reasonable timestamp
    timestamp = (
        doc.get("timestamp")
        or doc.get("logged")
        or doc.get("date")
        or doc.get("created_at")
    )

    title = doc.get("title") or doc.get("subject") or doc.get("note")

    content = (
        doc.get("content")
        or doc.get("notes")
        or doc.get("message")
        or doc.get("raw_fragment")
    )

    return Fragment(
        id=frag_id,
        collection=collection,
        type=doc.get("type") or default_type,
        title=title,
        subject=doc.get("subject"),
        tags=doc.get("tags", []),
        timestamp=timestamp,
        date=doc.get("date"),
        content=content,
        source=doc.get("source") or doc.get("source_system"),
    )


@router.get("/", response_model=List[Fragment])
def list_fragments(limit: int = 200) -> List[Fragment]:
    """
    Unified Phoenix Fragment Index.

    Returns fragments from all configured collections, normalized into a single schema,
    sorted by timestamp (most recent first).
    """
    fragments: List[Fragment] = []

    for collection, default_type in FRAGMENT_COLLECTIONS:
        # We sort by "date" where available; many of your docs use that.
        for doc in db[collection].find().sort("date", -1).limit(limit):
            fragments.append(_normalize_doc(doc, collection, default_type))

    # Global sort by timestamp string (best-effort, since legacy data is mixed)
    fragments.sort(key=lambda f: f.timestamp or "", reverse=True)

    return fragments[:limit]


@router.get("/{fragment_id}", response_model=Fragment)
def get_fragment(fragment_id: str) -> Fragment:
    """
    Look up a fragment by ID across all fragment collections.
    """
    for collection, default_type in FRAGMENT_COLLECTIONS:
        try:
            doc = db[collection].find_one({"_id": ObjectId(fragment_id)})
        except Exception:
            # Not a valid ObjectId, skip
            doc = None

        if doc:
            return _normalize_doc(doc, collection, default_type)

    raise HTTPException(status_code=404, detail="Fragment not found")


@router.get("/search/", response_model=List[Fragment])
def search_fragments(
    q: str = Query(..., description="Search text"),
    limit: int = 200,
) -> List[Fragment]:
    """
    Simple full-text-ish search across all fragment collections.

    Searches in title/subject/content/tags fields.
    """
    fragments: List[Fragment] = []

    query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"subject": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"notes": {"$regex": q, "$options": "i"}},
            {"message": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
        ]
    }

    for collection, default_type in FRAGMENT_COLLECTIONS:
        for doc in db[collection].find(query).limit(limit):
            fragments.append(_normalize_doc(doc, collection, default_type))

    fragments.sort(key=lambda f: f.timestamp or "", reverse=True)
    return fragments[:limit]


@router.get("/by_tag/{tag}", response_model=List[Fragment])
def fragments_by_tag(tag: str, limit: int = 200) -> List[Fragment]:
    """
    Return all fragments that contain a given tag.
    """
    fragments: List[Fragment] = []

    for collection, default_type in FRAGMENT_COLLECTIONS:
        for doc in db[collection].find({"tags": tag}).limit(limit):
            fragments.append(_normalize_doc(doc, collection, default_type))

    fragments.sort(key=lambda f: f.timestamp or "", reverse=True)
    return fragments[:limit]


@router.get("/by_type/{fragment_type}", response_model=List[Fragment])
def fragments_by_type(fragment_type: str, limit: int = 200) -> List[Fragment]:
    """
    Return fragments filtered by their type field.
    """
    fragments: List[Fragment] = []

    for collection, default_type in FRAGMENT_COLLECTIONS:
        for doc in db[collection].find({"type": fragment_type}).limit(limit):
            fragments.append(_normalize_doc(doc, collection, default_type))

    fragments.sort(key=lambda f: f.timestamp or "", reverse=True)
    return fragments[:limit]

