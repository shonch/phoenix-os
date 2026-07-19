# phoenix_portfolio/backend/engines/frisson_engine.py

from collections import Counter
from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db

Fragment = Dict[str, Any]

FRISSON_TAG_HINTS = {
    "frisson", "awe", "shiver", "goosebumps", "tears",
    "mythic", "sacred", "resonance", "electric", "charged",
    "cathedral", "mountain", "ocean", "cosmic", "ritual"
}

FRISSON_PHRASES = [
    "full-body shiver",
    "goosebumps",
    "tears in my eyes",
    "hair on my arms",
    "felt like a portal",
    "felt like a cathedral",
    "felt mythic",
    "felt sacred",
    "felt electric",
]


# ============================================================
#   FRISSON ENGINE — counts only
# ============================================================

def analyze_frisson_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    if not fragments:
        return {
            "intensity_profile": [],
            "triggers": [],
            "contexts": [],
        }

    intensity_counter = Counter()
    trigger_counter = Counter()
    context_counter = Counter()

    for frag in fragments:
        content = (frag.get("body") or frag.get("raw_text") or "").lower()
        tags = _extract_tags(frag)
        source = (frag.get("source") or "").lower()
        ctx = (frag.get("context") or frag.get("note") or "").lower()

        intensity = frag.get("intensity")
        if isinstance(intensity, (int, float)):
            bucket = _bucket_intensity(intensity)
            intensity_counter[bucket] += 1

        for t in tags:
            if t in FRISSON_TAG_HINTS:
                trigger_counter[t] += 1

        for phrase in FRISSON_PHRASES:
            if phrase in content:
                trigger_counter[phrase] += 1

        if "music" in source or "track" in content or "album" in content:
            context_counter["music"] += 1
        if "mountain" in content or "ridge" in content or "summit" in content:
            context_counter["mountain"] += 1
        if "ocean" in content or "sea" in content:
            context_counter["ocean"] += 1
        if "city" in content or "street" in content:
            context_counter["city"] += 1
        if ctx:
            context_counter["other"] += 1

    intensity_profile = [
        {"bucket": b, "count": c} for b, c in sorted(intensity_counter.items())
    ]
    triggers = [
        {"trigger": t, "count": c} for t, c in trigger_counter.most_common(15)
    ]
    contexts = [
        {"context": k, "count": v} for k, v in context_counter.most_common(10)
    ]

    return {
        "intensity_profile": intensity_profile,
        "triggers": triggers,
        "contexts": contexts,
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


def _bucket_intensity(value: float) -> str:
    if value >= 8:
        return "peak"
    if value >= 5:
        return "strong"
    if value >= 3:
        return "moderate"
    return "subtle"


def analyze_frisson(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_frisson_fragments.
    Loads emotional_fragments and filters for frisson-related content,
    checking the real body/raw_text fields (not legacy 'content').
    """
    docs = list(
        db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    )

    frisson_docs = []
    for d in docs:
        content = (d.get("body") or d.get("raw_text") or "").lower()
        tags = d.get("tags", [])
        tag_list = []

        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, dict):
                    name = t.get("tag_name") or t.get("name")
                    if name:
                        tag_list.append(str(name).lower())
                else:
                    tag_list.append(str(t).lower())
        elif isinstance(tags, dict):
            name = tags.get("tag_name") or tags.get("name")
            if name:
                tag_list.append(str(name).lower())
        elif isinstance(tags, str):
            tag_list.append(tags.lower())

        if any(hint in content for hint in FRISSON_TAG_HINTS) or any(
            hint in tag_list for hint in FRISSON_TAG_HINTS
        ):
            frisson_docs.append(d)

    return analyze_frisson_fragments(frisson_docs)
