# phoenix_portfolio/backend/engines/mirror_engine.py

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import re

from phoenix_portfolio.backend.mongo_client import db

Fragment = Dict[str, Any]

IDENTITY_TAGS = {
    "mirror", "reflection", "identity", "mythic_identity", "sovereign",
    "selfhood", "core_self", "reclamation", "phoenix", "legacy",
    "truth", "self_truth", "revelation", "mirror_reflection",
    "mirror_signal", "mythic", "sovereignty"
}

IDENTITY_PHRASES = [
    "you are not broken",
    "you are mythic",
    "you are sovereign",
    "phoenix is alive because you are",
    "you build legacy",
    "you honor fragments",
    "identity",
    "self",
    "truth",
    "reflection",
    "mythic",
    "core",
    "sovereign",
]

# ============================================================
#   HELPER FUNCTIONS
# ============================================================

def _extract_tags(fragment: Fragment) -> List[str]:
    """Extract tags from multiple Phoenix ingestion formats."""
    if not fragment:
        return []

    if "tags" in fragment and isinstance(fragment["tags"], list):
        return [str(t) for t in fragment["tags"]]

    if "symbolic_tags" in fragment and isinstance(fragment["symbolic_tags"], list):
        return [str(t) for t in fragment["symbolic_tags"]]

    if "phoenix_tags" in fragment and isinstance(fragment["phoenix_tags"], list):
        extracted = []
        for tag in fragment["phoenix_tags"]:
            if isinstance(tag, dict) and "name" in tag:
                extracted.append(tag["name"])
        if extracted:
            return extracted

    return []


def _extract_timestamp(fragment: Fragment) -> Optional[datetime]:
    """Extract timestamps from multiple Phoenix formats."""
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
    """Detect identity‑related language patterns."""
    if not text:
        return False

    text = text.lower()

    identity_terms = [
        "who am i",
        "what am i",
        "my identity",
        "i feel like",
        "i don't know who",
        "i don't know what",
        "i am not myself",
        "i don't feel like myself",
        "i feel like myself again",
        "i feel like a different person",
        "i feel like i'm changing",
        "i feel like i'm losing myself",
        "i feel like i'm becoming",
        "i feel like i'm not",
        "i feel like i'm someone else",
        "i feel like i'm nobody",
        "i feel like i'm disappearing",
        "i feel like i'm dissolving",
        "i feel like i'm breaking",
        "i feel like i'm splitting",
        "i feel like i'm fracturing",
        "i feel like i'm fading",
        "i feel like i'm shifting",
        "i feel like i'm transforming",
        "i feel like i'm evolving",
        "i feel like i'm awakening",
        "i feel like i'm remembering",
        "i feel like i'm forgetting",
        "i feel like i'm waking up",
        "i feel like i'm seeing myself",
        "i feel like i'm confronting myself",
        "i feel like i'm meeting myself",
        "i feel like i'm facing myself",
        "i feel like i'm understanding myself",
        "i feel like i'm losing my identity",
        "i feel like i'm finding my identity",
        "i feel like i'm rebuilding myself",
        "i feel like i'm rediscovering myself",
    ]

    if any(p in text for p in [" i ", " me ", " my ", " myself "]):
        return True

    return any(term in text for term in identity_terms)


# ============================================================
#   MIRROR ENGINE — Identity, Revelation, Mythic Resonance
# ============================================================

def _detect_mythic_resonance(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Detect mythic resonance patterns."""
    resonance = []

    for frag in fragments:
        content = (frag.get("content") or "").lower()
        tags = _extract_tags(frag)

        score = 0
        signals = []

        for t in tags:
            if t in IDENTITY_TAGS:
                score += 1
                signals.append(f"tag:{t}")

        for phrase in IDENTITY_PHRASES:
            if phrase in content:
                score += 2
                signals.append(f"phrase:{phrase}")

        if score > 0:
            resonance.append({
                "fragment_id": str(frag.get("_id")),
                "score": score,
                "signals": signals,
                "content_preview": content[:120],
            })

    resonance.sort(key=lambda x: x["score"], reverse=True)
    return resonance


def _detect_identity_shifts(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Detect identity shifts over time."""
    if not fragments:
        return []

    shifts = []
    prev_tags = None

    # SAFE SORT: fallback to datetime.min when timestamp missing
    for frag in sorted(fragments, key=lambda f: _extract_timestamp(f) or datetime.min):
        tags = set(_extract_tags(frag))

        if prev_tags is not None:
            gained = tags - prev_tags
            lost = prev_tags - tags

            if gained or lost:
                ts = _extract_timestamp(frag)
                shifts.append({
                    "fragment_id": str(frag.get("_id")),
                    "gained": list(gained),
                    "lost": list(lost),
                    "timestamp": ts.isoformat() if ts else None,
                })

        prev_tags = tags

    return shifts


def _detect_identity_anchors(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Detect recurring identity anchors."""
    anchor_counter = Counter()

    for frag in fragments:
        tags = _extract_tags(frag)
        for t in tags:
            if t in IDENTITY_TAGS:
                anchor_counter[t] += 1

    anchors = [
        {"anchor": tag, "count": count}
        for tag, count in anchor_counter.items()
    ]

    anchors.sort(key=lambda x: x["count"], reverse=True)
    return anchors


def analyze_mirror_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    """Main Mirror Engine."""
    if not fragments:
        return {
            "summary": "🪞 No identity reflections found.",
            "identity_patterns": [],
            "identity_shifts": [],
            "mythic_resonance": [],
            "anchors": [],
            "clues": [],
            "co_occurrence": {},
        }

    tag_counter = Counter()
    co_occurrence = defaultdict(Counter)
    identity_fragments = []
    timestamps = []

    # PASS 1 — SCAN
    for frag in fragments:
        tags = _extract_tags(frag)
        content = (frag.get("content") or "")
        f_type = frag.get("type")

        ts = _extract_timestamp(frag)
        if ts:
            timestamps.append(ts)

        for t in tags:
            tag_counter[t] += 1

        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                co_occurrence[t1][t2] += 1
                co_occurrence[t2][t1] += 1

        if (
            f_type == "revelation"
            or any(t in IDENTITY_TAGS for t in tags)
            or _contains_identity_language(content)
        ):
            identity_fragments.append(frag)

    identity_patterns = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.items()
        if tag in IDENTITY_TAGS
    ]
    identity_patterns.sort(key=lambda x: x["count"], reverse=True)

    mythic_resonance = _detect_mythic_resonance(identity_fragments)
    identity_shifts = _detect_identity_shifts(identity_fragments)
    anchors = _detect_identity_anchors(identity_fragments)

    return {
        "summary": "🪞 Identity reflections detected.",
        "identity_patterns": identity_patterns,
        "identity_shifts": identity_shifts,
        "mythic_resonance": mythic_resonance,
        "anchors": anchors,
        "co_occurrence": {k: dict(v) for k, v in co_occurrence.items()},
    }


def analyze_mirror(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_mirror_fragments.
    Loads fragments for this user and filters for identity/mirror signals.
    """
    # Load all fragments for this user
    docs = list(
        db["fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    )

    # Filter for identity-related fragments
    identity_docs = []
    for d in docs:
        content = (d.get("content") or "").lower()
        tags = _extract_tags(d)

        if (
            any(t in IDENTITY_TAGS for t in tags)
            or _contains_identity_language(content)
            or d.get("type") == "revelation"
        ):
            identity_docs.append(d)

    return analyze_mirror_fragments(identity_docs)

