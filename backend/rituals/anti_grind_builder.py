# phoenix_portfolio/backend/rituals/anti_grind_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest, Tag
from phoenix_portfolio.backend.modules.symbolic_tag import _normalize_legacy_fields
from datetime import datetime

def build_anti_grind_fragment(payload: dict) -> FragmentLogRequest:
    # --- Extract nested structure from builder.ts ---
    fragment = payload.get("fragment", {})
    metadata = fragment.get("metadata", {})
    raw_inputs = metadata.get("raw_inputs", [])
    symbolic_anchor = metadata.get("symbolic_anchor", "")
    tags = fragment.get("tags", []) or []
    ritual_type = payload.get("ritual_type", "anti_grind")

    # --- Build raw_text from step responses ---
    raw_text = "\n".join(
        str(step.get("text", "")) for step in raw_inputs if step.get("text")
    ).strip()

    # --- Build body (anti-grind tone: release, relief, unburdening) ---
    body = raw_text or f"Release: {symbolic_anchor}" or "Anti-grind fragment"

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
        module="anti_grind",
        layer="emotional",
        type=ritual_type,
        title=symbolic_anchor,
        subject=symbolic_anchor,
        raw_text=raw_text,
        body=body,
        tags=tag_objs,
        source="anti_grind_routes",
        metadata=metadata,
        extra={},
        version="phoenixos.v1.1",
        timestamp=datetime.utcnow(),
    )
