from datetime import datetime
from typing import List, Union

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
    Tag,
)

from phoenix_portfolio.phoenix_engine.models.tag import PhoenixTag
from phoenix_portfolio.backend.modules import symbolic_tag


def _resolve_collection(layer: str) -> str:
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

    normalized: List[PhoenixTag] = []

    for raw in raw_tags:
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
                "source_system": source_system,
            }
        else:
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
                "source_system": source_system,
            }

        tag_dict = symbolic_tag.create_tag(tag_data)

        if "_id" in tag_dict:
            tag_dict["id"] = str(tag_dict["_id"])
            del tag_dict["_id"]

        normalized.append(PhoenixTag(**tag_dict))

    return normalized


def ingest_fragment(req: FragmentLogRequest, user_id: str) -> FragmentResponse:
    now = datetime.utcnow()

    module = req.module
    frag_type = req.type
    layer = req.layer
    source_system = req.source or f"{module}_routes"

    phoenix_tags: List[PhoenixTag] = _normalize_tags_for_user(
        raw_tags=req.tags or [],
        user_id=user_id,
        source_system=source_system,
    )

    doc = {
        "module": module,
        "layer": layer,
        "type": frag_type,
        "title": req.title,
        "subject": req.subject,
        "raw_text": req.raw_text,
        "body": req.body,
        "tags": [t.name for t in phoenix_tags],
        "timestamp": now,
        "date": now.date().isoformat(),
        "source_system": source_system,
        "user_id": user_id,
        "metadata": req.metadata or {},
        "extra": req.extra or {},
        "version": req.version or "phoenixos.v1.1",
    }

    collection = _resolve_collection(layer)
    result = db[collection].insert_one(doc)
    doc["_id"] = result.inserted_id

    serialized = serialize_doc(doc)

    response_tags = [Tag(**t.dict()) for t in phoenix_tags]

    return FragmentResponse(
        id=serialized["id"],
        module=serialized["module"],
        layer=serialized["layer"],
        type=serialized["type"],
        title=serialized.get("title"),
        subject=serialized.get("subject"),
        raw_text=serialized.get("raw_text"),
        body=serialized.get("body"),
        tags=response_tags,
        source=serialized.get("source_system"),
        timestamp=serialized.get("timestamp"),
        metadata=serialized.get("metadata") or {},
        extra=serialized.get("extra") or {},
        version=serialized.get("version") or "phoenixos.v1.1",
    )

