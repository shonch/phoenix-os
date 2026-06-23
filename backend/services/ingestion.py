from datetime import datetime
from typing import Literal, List, Union

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
    Tag,
)

from phoenix_portfolio.phoenix_engine.models.tag import PhoenixTag
from phoenix_portfolio.backend.modules import symbolic_tag
from phoenix_portfolio.backend.modules.emotional_grammar import build_fragment


Layer = Literal["emotional", "revelation", "threshold"]


def _resolve_collection(layer: Layer) -> str:
    if layer == "emotional":
        return "emotional_fragments"
    if layer == "revelation":
        return "revelations"
    if layer == "threshold":
        return "thresholds"
    return "emotional_fragments"


def _normalize_tags_for_user(
    raw_tags: List[Union[str, Tag]],
    user_id: str,
    source_system: str,
) -> List[PhoenixTag]:
    """
    Normalize incoming tags (either simple strings or Tag objects)
    into fully-formed PhoenixTag instances, using symbolic_tag.create_tag
    as the persistence layer.

    This is the canonical bridge between API payloads and the PhoenixTag model.
    """
    normalized: List[PhoenixTag] = []

    for raw in raw_tags:
        # Simple string tag → generate defaults
        if isinstance(raw, str):
            name = raw
            tag_data = {
                "name": name,
                "user_id": user_id,
                "emoji": "🏷️",
                "category": "general",
                "description": "",
                "archetype": "none",
                "visibility": "public",
                "color": None,
                "emotional_weight": None,
                "sass_level": None,
                "dominatrix_affinity": None,
                "source_system": source_system,
            }
        else:
            # Tag object from API schema
            name = raw.label or raw.name
            tag_data = {
                "name": name,
                "user_id": user_id,
                "emoji": raw.emoji or "🏷️",
                "category": raw.category or "general",
                "description": raw.description or "",
                "archetype": raw.archetype or "none",
                "visibility": raw.visibility or "public",
                "color": raw.color,
                "emotional_weight": raw.emotional_weight,
                "sass_level": raw.sass_level,
                "dominatrix_affinity": raw.dominatrix_affinity,
                "source_system": source_system,
            }

        # Persist or update via symbolic_tag
        tag_dict = symbolic_tag.create_tag(tag_data)

        # Normalize Mongo _id → id for PhoenixTag
        if "_id" in tag_dict:
            tag_dict["id"] = str(tag_dict["_id"])
            del tag_dict["_id"]

        normalized.append(PhoenixTag(**tag_dict))

    return normalized


def ingest_fragment(req: FragmentLogRequest, user_id: str) -> FragmentResponse:
    """
    PhoenixOS v1 Unified Ingestion Pipeline:

    - normalize tags into PhoenixTag objects
    - build expressive fragment content via emotional_grammar
    - route to correct collection based on layer
    - persist full PhoenixOS envelope
    - return FragmentResponse
    """

    now = datetime.utcnow()

    module = req.module
    frag_type = req.type
    layer: Layer = req.layer
    source_system = req.source or f"{module}_routes"

    # 1) Normalize tags → PhoenixTag objects
    raw_tags = req.tags or []
    phoenix_tags: List[PhoenixTag] = _normalize_tags_for_user(
        raw_tags=raw_tags,
        user_id=user_id,
        source_system=source_system,
    )

    # 2) Build expressive content using emotional_grammar
    fragment_core = build_fragment(
        content=req.body or req.raw_text or "",
        title=req.title,
        subject=req.subject,
        fragment_type=frag_type,
        tags=[t.dict() for t in phoenix_tags],
    )

    # 3) Build PhoenixOS document envelope
    doc = {
        "module": module,
        "layer": layer,
        "type": frag_type,
        "title": fragment_core["title"],
        "subject": fragment_core["subject"],
        "raw_text": req.raw_text,
        "content": fragment_core["content"],
        "tags": [t.label for t in phoenix_tags],
        "timestamp": now,
        "date": now.date().isoformat(),
        "source_system": source_system,
        "user_id": user_id,
        "mode": req.mode,
        "metadata": req.metadata or {},
        "extra": req.extra or {},
        "version": req.version or "phoenixos.v1",
    }

    # 4) Persist
    collection = _resolve_collection(layer)
    result = db[collection].insert_one(doc)
    doc["_id"] = result.inserted_id

    serialized = serialize_doc(doc)

    # 5) Convert PhoenixTag → Tag for response
    response_tags = [Tag(**t.dict()) for t in phoenix_tags]

    return FragmentResponse(
        id=serialized["id"],
        collection=collection,
        type=serialized["type"],
        title=serialized.get("title"),
        subject=serialized.get("subject"),
        content=serialized.get("content"),
        tags=response_tags,
        timestamp=serialized.get("timestamp"),
        date=serialized.get("date"),
        source=serialized.get("source_system"),
    )

