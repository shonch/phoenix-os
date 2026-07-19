from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

Fragment = Dict[str, Any]

EMOTION_TAGS = {
    "joy", "sadness", "anger", "fear", "shame", "guilt",
    "hope", "calm", "peace", "anxiety", "overwhelm",
    "clarity", "fog", "drift", "stability", "exhaustion",
    "tension", "release", "relief", "confusion",
}

EMOTION_PHRASES = [
    "i feel", "i'm feeling", "im feeling", "emotionally", "it feels like",
    "i'm overwhelmed", "im overwhelmed", "i'm exhausted", "im exhausted",
    "i'm anxious", "im anxious",
    "i feel clear", "i feel foggy", "i feel lost",
    "i feel grounded", "i feel steady",
]

# ============================================================
#   EMOTION ENGINE — real counts, real fragment references, no interpretation
# ============================================================

def analyze_emotion_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    """
    Emotion Engine — counts only. No summary sentences, no interpretive claims.
    Every count links back to the actual fragments that produced it.
    """

    if not fragments:
        return {
            "dominant_emotions": [],
            "tag_frequency": [],
            "cycles": [],
        }

    emotion_occurrences: Dict[str, List[dict]] = defaultdict(list)
    tag_occurrences: Dict[str, List[dict]] = defaultdict(list)
    by_day = Counter()

    for frag in fragments:
        content = (frag.get("body") or frag.get("content") or "").lower()
        tags = _extract_tags(frag)
        ts = _extract_timestamp(frag)

        frag_ref = {
            "id": str(frag.get("_id") or frag.get("id") or ""),
            "date": ts.isoformat() if ts else None,
            "snippet": (frag.get("body") or frag.get("content") or "")[:160],
        }

        # Emotion-word matches (from tags AND raw content, since not every
        # entry uses a formal tag for a feeling word)
        for word in EMOTION_TAGS:
            if word in tags or word in content:
                emotion_occurrences[word].append(frag_ref)

        # Real tag frequency — ALL tags, not filtered to the emotion set.
        # Deliberately includes noisy/rough tags for now (e.g. oddly-specific
        # or comma-mangled ones) — this is expected until tag quality/
        # enrichment work happens; seeing the noise is how we'll know what
        # to fix.
        for t in tags:
            tag_occurrences[t].append(frag_ref)

        if ts:
            by_day[ts.date()] += 1

    dominant_emotions = [
        {"emotion": e, "count": len(refs), "fragments": refs}
        for e, refs in sorted(
            emotion_occurrences.items(), key=lambda kv: -len(kv[1])
        )
    ][:10]

    tag_frequency = [
        {"tag": t, "count": len(refs), "fragments": refs}
        for t, refs in sorted(
            tag_occurrences.items(), key=lambda kv: -len(kv[1])
        )
    ][:15]

    cycles = [
        {"day": d.isoformat(), "count": c}
        for d, c in sorted(by_day.items())
    ]

    return {
        "dominant_emotions": dominant_emotions,
        "tag_frequency": tag_frequency,
        "cycles": cycles,
    }

# ============================================================
#   HELPERS (unchanged)
# ============================================================

def _extract_tags(frag: Fragment) -> List[str]:
    raw = frag.get("tags", [])
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

    return [t.lower() for t in tags if t]


def _extract_timestamp(frag: Fragment) -> Optional[datetime]:
    value = (
        frag.get("timestamp")
        or frag.get("date")
        or frag.get("created_at")
        or frag.get("inserted_at")
    )
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None

# ============================================================
#   STATE ENGINE WRAPPER (unchanged)
# ============================================================

def analyze_emotion(user_id: str) -> Dict[str, Any]:
    fragments = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]
    return analyze_emotion_fragments(fragments)
