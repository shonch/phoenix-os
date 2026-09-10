# phoenix_portfolio/backend/engines/mirror_engine.py

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.mongo_client import db

Fragment = Dict[str, Any]

IDENTITY_TAGS = {
    "mirror", "reflection", "identity", "mythic_identity", "sovereign",
    "selfhood", "core_self", "reclamation", "phoenix", "legacy",
    "truth", "self_truth", "revelation", "mirror_reflection",
    "mirror_signal", "mythic", "sovereignty"
}

IDENTITY_PHRASES = [
    "who am i",
    "what am i",
    "my identity",
    "i don't know who i am",
    "i don't feel like myself",
    "i feel like a different person",
    "i feel like i'm changing",
    "i feel like i'm losing myself",
    "i feel like i'm becoming",
    "i feel like i'm someone else",
    "losing my identity",
    "finding my identity",
    "rebuilding myself",
    "rediscovering myself",
]


# ============================================================
#   HELPER FUNCTIONS
# ============================================================

def _extract_tags(fragment: Fragment) -> List[str]:
    if not fragment:
        return []

    raw = fragment.get("tags")
    if not isinstance(raw, list):
        return []

    tags: List[str] = []
    for t in raw:
        if isinstance(t, dict):
            name = t.get("name") or t.get("tag_name") or t.get("label")
            if name:
                tags.append(str(name).lower())
        else:
            tags.append(str(t).lower())

    return tags

def _extract_timestamp(fragment: Fragment) -> Optional[datetime]:
    if not fragment:
        return None

    ts = fragment.get("timestamp")
    if isinstance(ts, datetime):
        return ts

    for key in ["created_at", "ts", "date", "inserted_at"]:
        val = fragment.get(key)
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val)
            except Exception:
                pass

    return None


def _contains_identity_language(text: str) -> bool:
    if not text:
        return False
    text = text.lower()
    return any(term in text for term in IDENTITY_PHRASES)


# ============================================================
#   MIRROR ENGINE — real Mirror fragments as the primary list,
#   identity-tag/phrase tracking as a secondary, honestly-scoped
#   pattern within them.
# ============================================================

def analyze_mirror_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    if not fragments:
        return {
            "total": 0,
            "fragments": [],
            "identity_patterns": [],
            "identity_shifts": [],
            "anchors": [],
        }

    frag_refs = []
    tag_counter = Counter()

    for frag in fragments:
        content = frag.get("body") or frag.get("raw_text") or frag.get("content") or ""
        ts = _extract_timestamp(frag)

        frag_refs.append({
            "id": str(frag.get("_id") or frag.get("id") or ""),
            "date": ts.isoformat() if ts else None,
            "title": frag.get("title") or frag.get("subject"),
            "snippet": content[:160],
        })

        for t in _extract_tags(frag):
            tag_counter[t] += 1

    frag_refs.sort(key=lambda f: f["date"] or "", reverse=True)

    identity_patterns = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.items()
        if tag in IDENTITY_TAGS
    ]
    identity_patterns.sort(key=lambda x: x["count"], reverse=True)

    identity_shifts = _detect_identity_shifts(fragments)
    anchors = _detect_identity_anchors(fragments)

    return {
        "total": len(fragments),
        "fragments": frag_refs,
        "identity_patterns": identity_patterns,
        "identity_shifts": identity_shifts,
        "anchors": anchors,
    }


def _detect_identity_shifts(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Real, non-guessed structural pattern: which real tags appear on one
    Mirror fragment but not the next, across your actual Mirror fragments
    in chronological order."""
    if not fragments:
        return []

    shifts = []
    prev_tags = None

    for frag in sorted(fragments, key=lambda f: _extract_timestamp(f) or datetime.min):
        tags = set(_extract_tags(frag))

        if prev_tags is not None:
            gained = tags - prev_tags
            lost = prev_tags - tags

            if gained or lost:
                ts = _extract_timestamp(frag)
                shifts.append({
                    "fragment_id": str(frag.get("_id") or frag.get("id") or ""),
                    "gained": sorted(gained),
                    "lost": sorted(lost),
                    "timestamp": ts.isoformat() if ts else None,
                })

        prev_tags = tags

    return shifts


def _detect_identity_anchors(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Counts real tags from IDENTITY_TAGS across Mirror fragments only —
    not the whole archive, so this reflects identity language specifically
    within fragments you already classified as Mirror."""
    anchor_counter = Counter()

    for frag in fragments:
        for t in _extract_tags(frag):
            if t in IDENTITY_TAGS:
                anchor_counter[t] += 1

    anchors = [
        {"anchor": tag, "count": count}
        for tag, count in anchor_counter.items()
    ]
    anchors.sort(key=lambda x: x["count"], reverse=True)
    return anchors


def analyze_mirror(user_id: str) -> Dict[str, Any]:
    """
    Mirror fragments are real ritual data (layer="revelation") living in
    the revelations collection, filtered to type == "mirror" — real
    ground truth. Also checks emotional_fragments in case a Mirror
    fragment ever lands there.
    """
    revelations_docs = list(
        db["revelations"]
        .find({"user_id": user_id, "type": "mirror"})
        .sort("timestamp", -1)
    )

    current_docs = list(
        db["emotional_fragments"]
        .find({"user_id": user_id, "type": "mirror"})
        .sort("timestamp", -1)
    )

    return analyze_mirror_fragments(revelations_docs + current_docs)
