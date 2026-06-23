from typing import Dict, List, Any
from datetime import datetime, timedelta

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc


def compute_signals(buckets: Dict[str, List[dict]]) -> Dict[str, Any]:
    """
    Compute emotional, symbolic, mythic, and system signals
    from classified fragment buckets.
    """

    # -----------------------------
    # Helper: extract timestamps
    # -----------------------------
    def get_ts(doc: dict):
        ts = doc.get("timestamp") or doc.get("date") or doc.get("inserted_at")
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                return None
        return ts

    # -----------------------------
    # Helper: normalize tags
    # -----------------------------
    def get_tags(doc: dict) -> List[str]:
        raw = doc.get("tags", [])
        tags: List[str] = []

        if isinstance(raw, dict):
            name = raw.get("tag_name") or raw.get("name")
            if name:
                tags.append(str(name))
        elif isinstance(raw, list):
            for t in raw:
                if isinstance(t, dict):
                    name = t.get("tag_name") or t.get("name")
                    if name:
                        tags.append(str(name))
                else:
                    tags.append(str(t))
        elif isinstance(raw, str):
            tags.append(raw)

        return tags

    now = datetime.utcnow()

    # -----------------------------
    # Emotional signals
    # -----------------------------
    emotional_signals = {
        "rising": [],
        "fading": [],
        "active": [],
        "dormant": [],
        "unresolved": [],
        "anomalies": [],
    }

    for bucket_type, docs in buckets.items():
        if not docs:
            continue

        timestamps = [get_ts(d) for d in docs if get_ts(d)]
        if not timestamps:
            continue

        timestamps.sort(reverse=True)
        latest = timestamps[0]

        # Active if within 48 hours
        if now - latest < timedelta(hours=48):
            emotional_signals["active"].append(bucket_type)

        # Dormant if older than 30 days
        if now - latest > timedelta(days=30):
            emotional_signals["dormant"].append(bucket_type)

        # Rising/fading: compare last 5 vs previous 5
        if len(timestamps) >= 10:
            recent = timestamps[:5]
            older = timestamps[5:10]
            recent_span = recent[0] - recent[-1]
            older_span = older[0] - older[-1]
            if recent_span < older_span:
                emotional_signals["rising"].append(bucket_type)
            else:
                emotional_signals["fading"].append(bucket_type)

        # Unresolved: simple heuristic
        for d in docs:
            if d.get("unresolved") is True:
                emotional_signals["unresolved"].append(d)
                break

        # Anomalies: missing any timestamp field
        for d in docs:
            if "timestamp" not in d and "date" not in d and "inserted_at" not in d:
                emotional_signals["anomalies"].append(d)
                break

    # -----------------------------
    # Symbolic signals
    # -----------------------------
    symbolic_signals = {
        "evolving": [],
        "clusters": [],
    }

    tag_occurrences: Dict[str, set] = {}
    for bucket_type, docs in buckets.items():
        for d in docs:
            for tag in get_tags(d):
                tag_occurrences.setdefault(tag, set()).add(bucket_type)

    for tag, types in tag_occurrences.items():
        if len(types) > 1:
            symbolic_signals["evolving"].append(tag)

    # -----------------------------
    # Mythic signals
    # -----------------------------
    mythic_signals = {
        "active": [],
        "arcs": [],
    }

    mythic_docs = buckets.get("mythic", [])
    for d in mythic_docs:
        ts = get_ts(d)
        if ts and now - ts < timedelta(days=7):
            mythic_signals["active"].append(d)

    # -----------------------------
    # System signals
    # -----------------------------
    system_signals = {
        "warnings": [],
        "changes": [],
    }

    # -----------------------------
    # Final signal map
    # -----------------------------
    return {
        "emotional": emotional_signals,
        "symbolic": symbolic_signals,
        "mythic": mythic_signals,
        "system": system_signals,
    }


def analyze_signals(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for compute_signals.
    Loads fragments from Mongo, buckets them, and computes signals.
    """

    # Load all fragments for this user, serialized
    docs = [
        serialize_doc(d)
        for d in db["fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    # Bucket by fragment type
    buckets: Dict[str, List[dict]] = {}
    for d in docs:
        t = d.get("type") or d.get("fragment_type") or "unknown"
        buckets.setdefault(t, []).append(d)

    return compute_signals(buckets)

