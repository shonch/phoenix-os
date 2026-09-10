# phoenix_portfolio/backend/engines/threshold_emerge_engine.py

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.mongo_client import db
from backend.utils.serialization import serialize_doc

Fragment = Dict[str, Any]


def _extract_timestamp(frag: Fragment) -> Optional[datetime]:
    value = frag.get("timestamp") or frag.get("date") or frag.get("created_at")
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def analyze_thresholds(user_id: str) -> Dict[str, Any]:
    """
    Real Threshold fragments, gathered from every collection that can
    hold them (thresholds is the dedicated collection; emotional_fragments
    is checked too since a Threshold fragment could land there depending
    on how the layer/type combination ends up stored).
    """
    threshold_docs = [
        serialize_doc(d)
        for d in db["thresholds"].find({"user_id": user_id}).sort("timestamp", -1)
    ]

    other_docs = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id, "type": "threshold"})
        .sort("timestamp", -1)
    ]

    all_docs = threshold_docs + other_docs

    frag_refs = []
    fatigue = []

    for f in all_docs:
        content = f.get("body") or f.get("raw_text") or f.get("content") or ""
        tags = " ".join(str(t) for t in (f.get("tags") or []))
        ts = _extract_timestamp(f)

        frag_ref = {
            "id": str(f.get("_id") or f.get("id") or ""),
            "date": ts.isoformat() if ts else None,
            "title": f.get("title") or f.get("subject"),
            "snippet": content[:160],
        }
        frag_refs.append(frag_ref)

        joined = f"{content} {tags}".lower()
        if "fatigue" in joined:
            fatigue.append(frag_ref)

    frag_refs.sort(key=lambda f: f["date"] or "", reverse=True)
    fatigue.sort(key=lambda f: f["date"] or "", reverse=True)

    return {
        "total": len(all_docs),
        "fragments": frag_refs,
        "fatigue_trace_count": len(fatigue),
        "fatigue_traces": fatigue,
    }
