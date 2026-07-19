# phoenix_portfolio/backend/rituals/emotion_builder.py
from phoenix_portfolio.backend.modules.symbolic_tag import _normalize_legacy_fields
from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest, Tag
from datetime import datetime

def build_emotion_fragment(payload: dict) -> FragmentLogRequest:
    # --- Extract nested structure from builder.ts ---
    fragment = payload.get("fragment", {})
    metadata = fragment.get("metadata", {})
    raw_inputs = metadata.get("raw_inputs", [])
    symbolic_anchor = metadata.get("symbolic_anchor", "")
    tags = fragment.get("tags", []) or []
    ritual_type = payload.get("ritual_type", "emotion")

    # --- Build raw_text from step responses ---
    raw_text = "\n".join(
        str(step.get("text", "")) for step in raw_inputs if step.get("text")
    ).strip()

    # --- Build body (main emotional content) ---
    body = raw_text or symbolic_anchor or "Emotional fragment"

    # --- Convert incoming tag dicts into Tag objects ---
    # --- Convert incoming tag dicts into Tag objects ---
    tag_objs = []
    for t in tags:
        if isinstance(t, str):
            tag_objs.append(Tag(name=t))
        else:
            clean = _normalize_legacy_fields(dict(t))
            tag_objs.append(
                Tag(
                    name=clean.get("name") or clean.get("label") or "",
                    emoji=clean.get("emoji"),
                    category=clean.get("category"),
                    description=clean.get("description"),
                    archetype=clean.get("archetype"),
                    visibility=clean.get("visibility"),
                    color=clean.get("color"),
                    emotional_weight=clean.get("emotional_weight"),
                    user_id=clean.get("user_id"),
                )
            )

    # --- Construct FragmentLogRequest ---
    return FragmentLogRequest(
        module="emotion",          # module identity
        layer="emotional",         # collection: emotional_fragments
        type=ritual_type,          # classifier result
        title=symbolic_anchor,
        subject=symbolic_anchor,
        raw_text=raw_text,
        body=body,
        tags=tag_objs,
        source="emotion_routes",
        metadata=metadata,
        extra={},
        version="phoenixos.v1.1",
        timestamp=datetime.utcnow(),   # ⭐ REQUIRED FIX
    )

