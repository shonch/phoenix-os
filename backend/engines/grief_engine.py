# phoenix_portfolio/backend/engines/grief_engine.py

from datetime import datetime
from typing import Any, Dict, List

from backend.mongo_client import db
from backend.utils.adapter import (
    NormalizedFragment,
    normalize_fragment,
)


def _load_emotional_fragments(user_id: str) -> List[NormalizedFragment]:
    docs = list(db["emotional_fragments"].find({"user_id": user_id}))
    return [normalize_fragment(d, "emotional_fragments") for d in docs]


def analyze_grief(user_id: str) -> Dict[str, Any]:
    """
    Grief was never one of Phoenix's real ritual types, so this is
    honestly a keyword SEARCH across your archive for moments where
    the word "grief" surfaces — even briefly, inside a fragment that's
    really about something else — not a real category like Emotion or
    Mirror. Labeled "Traces of Grief" for that reason.
    """
    frags = _load_emotional_fragments(user_id)

    traces: List[NormalizedFragment] = []
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
            traces.append(f)

    traces_sorted = sorted(
        traces,
        key=lambda x: x.timestamp or datetime.min,
        reverse=True,
    )

    return {
        "label": "Traces of Grief",
        "total_scanned": len(frags),
        "trace_count": len(traces),
        "traces": [
            {
                "id": f.id,
                "subject": f.subject,
                "date": f.date_raw,
                "tags": f.tags,
                "type": getattr(f, "type", None),
                "snippet": (f.content or "")[:160],
            }
            for f in traces_sorted
        ],
    }
