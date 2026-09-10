from typing import Dict, List, Any
from datetime import datetime, timedelta

from backend.mongo_client import db
from backend.utils.serialization import serialize_doc

# The 8 real ritual types — anything outside this set is legacy/test
# debris from earlier architecture, not a meaningful ongoing category.
REAL_RITUAL_TYPES = {
    "emotion", "detective", "mirror", "grind", "anti_grind",
    "threshold", "emerge", "pulse",
}


def compute_signals(buckets: Dict[str, List[dict]]) -> Dict[str, Any]:
    """
    Emotional and symbolic signals — scoped to real ritual types only.
    Legacy/test type values (test_fragment, migration_complete, etc.)
    are excluded entirely rather than shown as if they're meaningful
    ongoing categories.
    """

    def get_ts(doc: dict):
        ts = doc.get("timestamp") or doc.get("date") or doc.get("inserted_at")
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                return None
        return ts

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

    real_buckets = {k: v for k, v in buckets.items() if k in REAL_RITUAL_TYPES}

    emotional_signals = {
        "rising": [],
        "fading": [],
        "active": [],
        "dormant": [],
        "recent": [],
    }

    for bucket_type, docs in real_buckets.items():
        if not docs:
            continue

        timestamps = [get_ts(d) for d in docs if get_ts(d)]
        if not timestamps:
            continue

        timestamps.sort(reverse=True)
        latest = timestamps[0]

        if now - latest < timedelta(hours=48):
            emotional_signals["active"].append(bucket_type)
        elif now - latest > timedelta(days=30):
            emotional_signals["dormant"].append(bucket_type)
        else:
            emotional_signals["recent"].append(bucket_type)


        if len(timestamps) >= 10:
            recent = timestamps[:5]
            older = timestamps[5:10]
            recent_span = recent[0] - recent[-1]
            older_span = older[0] - older[-1]
            if recent_span < older_span:
                emotional_signals["rising"].append(bucket_type)
            else:
                emotional_signals["fading"].append(bucket_type)

    # Evolving Tags: real tags that appear on fragments across 2+ of the
    # REAL ritual types — a genuine cross-ritual pattern, not a coincidence
    # with legacy/test data.
    tag_occurrences: Dict[str, set] = {}
    for bucket_type, docs in real_buckets.items():
        for d in docs:
            for tag in get_tags(d):
                tag_occurrences.setdefault(tag, set()).add(bucket_type)

    evolving_tags = [
        {"tag": tag, "ritual_types": sorted(types)}
        for tag, types in tag_occurrences.items()
        if len(types) > 1
    ]
    evolving_tags.sort(key=lambda t: -len(t["ritual_types"]))

    legacy_type_count = sum(len(v) for k, v in buckets.items() if k not in REAL_RITUAL_TYPES)

    return {
        "emotional": emotional_signals,
        "evolving_tags": evolving_tags,
        "legacy_fragments_excluded": legacy_type_count,
    }


def analyze_signals(user_id: str) -> Dict[str, Any]:
    """
    Loads from all real ritual collections (fragments kept for legacy-type
    counting/transparency, but excluded from the real signal computation).
    """
    collections_to_scan = ["fragments", "emotional_fragments", "revelations", "thresholds"]

    docs: List[dict] = []
    for coll_name in collections_to_scan:
        docs.extend(
            serialize_doc(d)
            for d in db[coll_name]
            .find({"user_id": user_id})
            .sort("timestamp", -1)
        )

    buckets: Dict[str, List[dict]] = {}
    for d in docs:
        t = (d.get("type") or d.get("fragment_type") or "unknown").lower()
        buckets.setdefault(t, []).append(d)



    return compute_signals(buckets)
