# phoenix_portfolio/backend/services/emotion_ingestion.py

from datetime import datetime
from typing import List

from ..schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
    Tag,
)

# PhoenixTag lives in phoenix_engine, not backend
from ...phoenix_engine.models.tag import PhoenixTag

from ..persistence.fragments import insert_fragment
from ..modules import symbolic_tag
from ..modules.emotional_grammar import build_fragment


def _phoenix_tag_from_dict(tag_dict: dict) -> PhoenixTag:
    """
    Helper: ensure Mongo-style tag dict becomes a PhoenixTag instance.
    Handles presence of _id and any legacy fields already normalized
    by symbolic_tag.
    """
    # We don't want Mongo's _id inside the model
    tag_dict = dict(tag_dict)
    tag_dict.pop("_id", None)
    return PhoenixTag(**tag_dict)


def normalize_tags(incoming_tags: List[Tag]) -> List[PhoenixTag]:
    """
    Normalize incoming Tag objects into canonical PhoenixTag objects.

    Rules:
    - If a tag already exists (by tag_id), load it.
    - Otherwise, create/update via symbolic_tag.create_tag using name + user_id.
    - Always return full PhoenixTag objects.
    """
    normalized: List[PhoenixTag] = []

    for t in incoming_tags:
        t_dict = t.dict()

        # Prefer explicit user_id on the tag; fall back to "system"
        user_id = t_dict.get("user_id") or "shonh@icloud.com"


        # If we ever extend Tag to include tag_id, we can resolve by that.
        tag_id = t_dict.get("tag_id")

        existing = None
        if tag_id:
            # Resolve by Phoenix tag_id (UUID), not Mongo _id
            matches = symbolic_tag.select_tag({"tag_id": tag_id})
            if matches:
                existing = matches[0]

        if existing is None:
            # Create or update by (label, user_id) via create_tag
            created = symbolic_tag.create_tag(
                {
                    "name": t_dict["name"],
                    "user_id": user_id,
                    "emoji": t_dict.get("emoji"),
                    "category": t_dict.get("category"),
                    "description": t_dict.get("description"),
                    "archetype": t_dict.get("archetype"),
                    "visibility": t_dict.get("visibility"),
                    # expressive / optional fields can be added here later
                    "source_system": "api",
                }
            )
            normalized.append(_phoenix_tag_from_dict(created))
        else:
            normalized.append(_phoenix_tag_from_dict(existing))

    return normalized


def build_fragment_document(
    req: FragmentLogRequest,
    normalized_tags: List[PhoenixTag],
) -> dict:
    """
    Build the canonical fragment document using the emotional grammar engine
    and store tag *IDs* (Phoenix tag_id), not full tag objects.
    """
    now = datetime.utcnow()

    # Let emotional_grammar shape the expressive core
    fragment_core = build_fragment(
        content=req.body,          # body is the main text content
        title=req.title,
        subject=req.subject,
        fragment_type=req.type,
        tags=[t.dict() for t in normalized_tags],
    )

    fragment_doc = {
        "collection": "emotional_fragments",
        # Core identity
        "module": req.module,
        "layer": req.layer,
        "type": fragment_core.get("type", req.type),
        # Content
        "title": fragment_core.get("title", req.title),
        "subject": fragment_core.get("subject", req.subject),
        "raw_text": req.raw_text,
        "body": fragment_core.get("content", req.body),
        # Tags: store ONLY tag IDs in the fragment
        "tags": [t.tag_id for t in normalized_tags],
        # Optionally store resolved tags for convenience / debugging
        "resolved_tags": [t.dict() for t in normalized_tags],
        # Metadata
        "timestamp": now,
        "source": req.source or "api",
        "metadata": req.metadata or {},
        "extra": req.extra or {},
        "version": req.version,
    }

    return fragment_doc


def ingest_fragment(req: FragmentLogRequest) -> FragmentResponse:
    """
    Full ingestion pipeline:
    - normalize tags (objects → PhoenixTag)
    - build expressive fragment document
    - persist fragment
    - return FragmentResponse with full tag objects
    """
    # NOTE: this assumes FragmentLogRequest.tags is a List[Tag] (objects),
    # not List[str]. The frontend will send full tag objects (even if some
    # fields are null), and ingestion will create/reuse tags as needed.
    normalized_tags = normalize_tags(req.tags)

    fragment_doc = build_fragment_document(req, normalized_tags)
    fragment_id = insert_fragment(fragment_doc)

    return FragmentResponse(
        id=fragment_id,
        # Core identity
        module=fragment_doc["module"],
        layer=fragment_doc["layer"],
        type=fragment_doc["type"],
        # Content
        title=fragment_doc.get("title"),
        subject=fragment_doc.get("subject"),
        raw_text=fragment_doc.get("raw_text"),
        body=fragment_doc["body"],
        # Tags: return full objects to the frontend
        tags=[Tag(**t.dict()) for t in normalized_tags],
        # Metadata
        source=fragment_doc["source"],
        timestamp=fragment_doc["timestamp"],
        metadata=fragment_doc.get("metadata", {}),
        extra=fragment_doc.get("extra", {}),
        version=fragment_doc.get("version", req.version),
    )

