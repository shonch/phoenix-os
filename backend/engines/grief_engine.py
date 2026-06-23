# phoenix_portfolio/backend/engines/grief_engine.py

from datetime import datetime
from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.adapter import (
    NormalizedFragment,
    normalize_fragment,
)


def _load_emotional_fragments(user_id: str) -> List[NormalizedFragment]:
    docs = list(db["emotional_fragments"].find({"user_id": user_id}))
    return [normalize_fragment(d, "emotional_fragments") for d in docs]


def analyze_grief(user_id: str) -> Dict[str, Any]:
    frags = _load_emotional_fragments(user_id)

    grief_related: List[NormalizedFragment] = []
    for f in frags:
        text_bits = [
            " ".join(f.tags or []),
            f.subject or "",
            f.content or "",
            f.theme or "",
            f.note or "",
        ]
        joined = " ".join(text_bits).lower()
        if "grief" in joined:
            grief_related.append(f)

    grief_sorted = sorted(
        grief_related,
        key=lambda x: x.timestamp or datetime.min,
        reverse=True,
    )

    return {
        "total_emotional_fragments": len(frags),
        "grief_events": len(grief_related),
        "recent_grief": [
            {
                "id": f.id,
                "subject": f.subject,
                "date": f.date_raw,
                "tags": f.tags,
                "weather": f.weather,
            }
            for f in grief_sorted[:10]
        ],
    }

