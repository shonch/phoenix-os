from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.mongo_client import db
from backend.utils.serialization import serialize_doc

Fragment = Dict[str, Any]

EMOTION_TAGS = {
    "joy", "sadness", "anger", "fear", "shame", "guilt",
    "hope", "calm", "peace", "anxiety", "overwhelm",
    "clarity", "fog", "drift", "stability", "exhaustion",
    "tension", "release", "relief", "confusion",
}

# ============================================================
#   EMOTION ENGINE — real fragments first, keyword words as a
#   secondary, honestly-labeled stat only.
# ============================================================

def analyze_emotion_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    """
    Primary: every fragment whose real ritual type is "emotion" —
    ground truth the user stated by picking that stone.
    Secondary: which words from a fixed list recur across that text —
    labeled as recurring words, not as emotional categories.
    """

    emotion_fragments = [f for f in fragments if (f.get("type") or "").lower() == "emotion"]

    if not emotion_fragments:
        return {
            "total": 0,
            "fragments": [],
            "recurring_words": [],
            "cycles": [],
            "trend_label": None,
        }

    word_occurrences: Dict[str, List[dict]] = defaultdict(list)
    by_day = Counter()
    frag_refs = []

    for frag in emotion_fragments:
        content = (frag.get("body") or frag.get("raw_text") or "").lower()
        tags = _extract_tags(frag)
        ts = _extract_timestamp(frag)

        frag_ref = {
            "id": str(frag.get("_id") or frag.get("id") or ""),
            "date": ts.isoformat() if ts else None,
            "title": frag.get("title") or frag.get("subject"),
            "snippet": (frag.get("body") or frag.get("raw_text") or "")[:160],
        }
        frag_refs.append(frag_ref)

        for word in EMOTION_TAGS:
            if word in tags or word in content:
                word_occurrences[word].append(frag_ref)

        if ts:
            by_day[ts.date()] += 1

    frag_refs.sort(key=lambda f: f["date"] or "", reverse=True)

    recurring_words = [
        {"word": w, "count": len(refs), "fragments": refs}
        for w, refs in sorted(word_occurrences.items(), key=lambda kv: -len(kv[1]))
    ][:10]

    cycles = [
        {"day": d.isoformat(), "count": c}
        for d, c in sorted(by_day.items())
    ]

    return {
        "total": len(emotion_fragments),
        "fragments": frag_refs,
        "recurring_words": recurring_words,
        "cycles": cycles,
        "trend_label": _trend_label(recurring_words, cycles),
    }

# ============================================================
#   HELPERS
# ============================================================

def _trend_label(recurring_words: List[dict], cycles: List[dict]) -> Optional[str]:
    if not recurring_words:
        return None

    top = recurring_words[0]["word"]

    if len(cycles) >= 2:
        recent = sum(c["count"] for c in cycles[-3:])
        earlier = sum(c["count"] for c in cycles[-6:-3]) if len(cycles) >= 6 else None
        if earlier is not None:
            if recent > earlier:
                return f"{top}, more present lately"
            if recent < earlier:
                return f"{top}, easing lately"

    return top

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
#   STATE ENGINE WRAPPER
# ============================================================

def analyze_emotion(user_id: str) -> Dict[str, Any]:
    """
    Loads from emotional_fragments AND revelations — both can hold real
    ritual data (emotion writes to emotional_fragments; this also checks
    revelations in case type ever appears there) — and filters to
    type == "emotion" as the real, ground-truth criterion.
    """
    fragments = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]
    return analyze_emotion_fragments(fragments)
