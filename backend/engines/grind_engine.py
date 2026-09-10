# phoenix_portfolio/backend/engines/grind_engine.py

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.mongo_client import db
from backend.utils.serialization import serialize_doc


Fragment = Dict[str, Any]


# ============================================================
#   GRIND ENGINE — real fragments first, structural patterns
#   (no made-up fields) as secondary.
# ============================================================

def analyze_grind_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    if not fragments:
        return {
            "total": 0,
            "grind_fragments": [],
            "release_fragments": [],
            "patterns": [],
            "cycles": [],
            "fatigue_signal": None,
        }

    tag_counter = Counter()
    grind_frags: List[dict] = []
    release_frags: List[dict] = []

    for frag in fragments:
        f_type = (frag.get("type") or "").lower()

        frag_ref = {
            "id": str(frag.get("_id") or frag.get("id") or ""),
            "date": (frag.get("date") or frag.get("timestamp")),
            "title": frag.get("title") or frag.get("subject"),
            "snippet": (frag.get("body") or frag.get("raw_text") or "")[:160],
        }

        if f_type in ("grind", "grind_scan"):
            grind_frags.append(frag_ref)
        elif f_type in ("anti_grind", "grind_override"):
            release_frags.append(frag_ref)

        for t in _extract_tags(frag):
            tag_counter[t] += 1

    grind_frags.sort(key=lambda f: f["date"] or "", reverse=True)
    release_frags.sort(key=lambda f: f["date"] or "", reverse=True)

    patterns = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.most_common(15)
    ]

    cycles = _detect_cycles(fragments)
    fatigue_signal = _detect_fatigue_signal(grind_frags)

    return {
        "total": len(grind_frags) + len(release_frags),
        "grind_fragments": grind_frags,
        "release_fragments": release_frags,
        "patterns": patterns,
        "cycles": cycles,
        "fatigue_signal": fatigue_signal,
    }


# ============================================================
#   HELPERS
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


def _parse_ts(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def _extract_timestamp(frag: Fragment) -> Optional[datetime]:
    for key in ["timestamp", "date", "created_at", "inserted_at"]:
        parsed = _parse_ts(frag.get(key))
        if parsed:
            return parsed
    return None


def _detect_cycles(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Real structural pattern: how long between a Grind fragment and the
    next Release (anti_grind) fragment after it — a genuine, non-guessed
    signal, since it's just comparing real timestamps."""
    events = []
    for f in fragments:
        f_type = (f.get("type") or "").lower()
        ts = _extract_timestamp(f)
        if not ts:
            continue
        if f_type in ("grind", "grind_scan"):
            events.append((ts, "grind", f))
        elif f_type in ("anti_grind", "grind_override"):
            events.append((ts, "release", f))

    events.sort(key=lambda x: x[0])

    cycles = []
    for i in range(len(events) - 1):
        ts1, t1, f1 = events[i]
        ts2, t2, f2 = events[i + 1]
        if t1 == "grind" and t2 == "release":
            delta = ts2 - ts1
            cycles.append({
                "grind_id": str(f1.get("_id") or f1.get("id") or ""),
                "release_id": str(f2.get("_id") or f2.get("id") or ""),
                "days_between": round(delta.total_seconds() / 86400, 1),
                "grind_date": f1.get("date") or f1.get("timestamp"),
                "release_date": f2.get("date") or f2.get("timestamp"),
            })

    return cycles


def _detect_fatigue_signal(grind_frags: List[dict]) -> Optional[Dict[str, Any]]:
    """
    Structural signal only — no guessed fields. Compares how many real
    Grind fragments landed in the most recent 14 days vs. the 14 days
    before that. A genuine frequency pattern in when you actually wrote,
    not an inference about how you felt.
    """
    now = datetime.utcnow()
    recent_cutoff = now - timedelta(days=14)
    prior_cutoff = now - timedelta(days=28)

    recent_count = 0
    prior_count = 0

    for f in grind_frags:
        ts = _parse_ts(f["date"])
        if not ts:
            continue
        if ts >= recent_cutoff:
            recent_count += 1
        elif ts >= prior_cutoff:
            prior_count += 1

    if recent_count == 0 and prior_count == 0:
        return None

    return {
        "recent_14_days": recent_count,
        "prior_14_days": prior_count,
        "trend": "rising" if recent_count > prior_count else ("easing" if recent_count < prior_count else "steady"),
    }


def analyze_grind(user_id: str) -> Dict[str, Any]:
    """
    Loads grind/anti_grind fragments from emotional_fragments (current
    pipeline), plus legacy grind_scan/grind_override fragments from the
    old fragments collection, so both old and new data are visible.
    """
    current_docs = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id, "type": {"$in": ["grind", "anti_grind"]}})
        .sort("timestamp", -1)
    ]

    legacy_docs = [
        serialize_doc(d)
        for d in db["fragments"]
        .find({"user_id": user_id, "type": {"$in": ["grind_scan", "grind_override"]}})
        .sort("timestamp", -1)
    ]

    return analyze_grind_fragments(current_docs + legacy_docs)
