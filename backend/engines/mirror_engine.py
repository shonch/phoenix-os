# phoenix_portfolio/backend/engines/mirror_engine.py

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from phoenix_portfolio.backend.mongo_client import db

Fragment = Dict[str, Any]

IDENTITY_TAGS = {
    "mirror", "reflection", "identity", "mythic_identity", "sovereign",
    "selfhood", "core_self", "reclamation", "phoenix", "legacy",
    "truth", "self_truth", "revelation", "mirror_reflection",
    "mirror_signal", "mythic", "sovereignty"
}

# Phrases a user might plausibly write themselves, about self-perception.
# (Previous version accidentally used second-person affirmation phrases
# like "you are mythic" — those are things Phoenix might say TO a user,
# not things a user would write about themselves, so they never matched
# anything real. Replaced with first-person self-reflection language.)
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

    if "tags" in fragment and isinstance(fragment["tags"], list):
        return [str(t).lower() for t in fragment["tags"]]

    if "symbolic_tags" in fragment and isinstance(fragment["symbolic_tags"], list):
        return [str(t).lower() for t in fragment["symbolic_tags"]]

    if "phoenix_tags" in fragment and isinstance(fragment["phoenix_tags"], list):
        extracted = []
        for tag in fragment["phoenix_tags"]:
            if isinstance(tag, dict) and "name" in tag:
                extracted.append(str(tag["name"]).lower())
        if extracted:
            return extracted

    return []


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
    """
    Detect identity-related language. Previous version matched on any
    occurrence of " i ", " me ", " my ", " myself " — which is true of
    almost every first-person sentence ever written, so it matched
    nearly everything. Now requires an actual identity-related phrase.
    """
    if not text:
        return False

    text = text.lower()
    return any(term in text for term in IDENTITY_PHRASES)


# ============================================================
#   MIRROR ENGINE — counts and structural pattern detection only
# ============================================================

def _detect_mythic_resonance(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Count identity-tag/phrase matches per fragment. `match_count` is a
    literal count of matches, not a judgment of significance."""
    resonance = []

    for frag in fragments:
        content = (frag.get("content") or frag.get("body") or "").lower()
        tags = _extract_tags(frag)

        match_count = 0
        signals = []

        for t in tags:
            if t in IDENTITY_TAGS:
                match_count += 1
                signals.append(f"tag:{t}")

        for phrase in IDENTITY_PHRASES:
            if phrase in content:
                match_count += 1
                signals.append(f"phrase:{phrase}")

        if match_count > 0:
            resonance.append({
                "fragment_id": str(frag.get("_id") or frag.get("id") or ""),
                "match_count": match_count,
                "signals": signals,
                "content_preview": content[:160],
            })

    resonance.sort(key=lambda x: x["match_count"], reverse=True)
    return resonance


def _detect_identity_shifts(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Detect changes in tag sets between consecutive fragments over time."""
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
                    "gained": list(gained),
                    "lost": list(lost),
                    "timestamp": ts.isoformat() if ts else None,
                })

        prev_tags = tags

    return shifts


def _detect_identity_anchors(fragments: List[Fragment]) -> List[Dict[str, Any]]:
    """Count recurring identity tags."""
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
    if not fragments:
        return {
            "identity_patterns": [],
            "identity_shifts": [],
            "mythic_resonance": [],
            "anchors": [],
            "co_occurrence": {},
        }

    tag_counter = Counter()
    co_occurrence = defaultdict(Counter)
    identity_fragments = []

    for frag in fragments:
        tags = _extract_tags(frag)
        content = frag.get("content") or frag.get("body") or ""
        f_type = frag.get("type")

        for t in tags:
            tag_counter[t] += 1

        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                co_occurrence[t1][t2] += 1
                co_occurrence[t2][t1] += 1

        if (
            f_type == "mirror"
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
        "identity_patterns": identity_patterns,
        "identity_shifts": identity_shifts,
        "mythic_resonance": mythic_resonance,
        "anchors": anchors,
        "co_occurrence": {k: dict(v) for k, v in co_occurrence.items()},
    }


def analyze_mirror(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_mirror_fragments.
    Loads from both the current ritual pipeline's collection
    (emotional_fragments, type='mirror') and the legacy 'fragments'
    collection, so old and new mirror-flavored data are both visible.
    """
    current_docs = list(
        db["emotional_fragments"]
        .find({"user_id": user_id, "type": "mirror"})
        .sort("timestamp", -1)
    )

    legacy_docs = list(
        db["fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    )

    identity_docs = []
    for d in legacy_docs:
        content = (d.get("content") or "").lower()
        tags = _extract_tags(d)

        if (
            any(t in IDENTITY_TAGS for t in tags)
            or _contains_identity_language(content)
            or d.get("type") == "revelation"
        ):
            identity_docs.append(d)

    return analyze_mirror_fragments(current_docs + identity_docs)
