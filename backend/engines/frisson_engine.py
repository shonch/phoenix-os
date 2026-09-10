# phoenix_portfolio/backend/engines/frisson_engine.py

from collections import Counter
from typing import Any, Dict, List

from backend.mongo_client import db

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
#   FRISSON ENGINE — like Grief, this is a keyword SEARCH across
#   your archive, not a real ritual category (Frisson isn't one
#   of the 8 ritual types). Labeled "Traces of Frisson" for that
#   reason. Note some hints (mountain, ritual, mythic) are common
#   words in normal writing, so a trace doesn't always mean a real
#   frisson moment — treat this as a starting point to look at,
#   not a confirmed count.
# ============================================================

def analyze_frisson_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    if not fragments:
        return {
            "label": "Traces of Frisson",
            "total_scanned": 0,
            "trace_count": 0,
            "traces": [],
            "triggers": [],
            "contexts": [],
        }

    trigger_counter = Counter()
    context_counter = Counter()
    traces = []

    for frag in fragments:
        content = (frag.get("body") or frag.get("raw_text") or "").lower()
        tags = _extract_tags(frag)

        matched_hints = [t for t in tags if t in FRISSON_TAG_HINTS]
        matched_phrases = [p for p in FRISSON_PHRASES if p in content]

        if not matched_hints and not matched_phrases:
            continue

        traces.append({
            "id": str(frag.get("_id") or frag.get("id") or ""),
            "subject": frag.get("title") or frag.get("subject"),
            "date": frag.get("date") or frag.get("timestamp"),
            "type": frag.get("type"),
            "snippet": (frag.get("body") or frag.get("raw_text") or "")[:160],
            "matched": matched_hints + matched_phrases,
        })

        for t in matched_hints:
            trigger_counter[t] += 1
        for p in matched_phrases:
            trigger_counter[p] += 1

        if "music" in (frag.get("source") or "").lower() or "track" in content or "album" in content:
            context_counter["music"] += 1
        if "mountain" in content or "ridge" in content or "summit" in content:
            context_counter["mountain"] += 1
        if "ocean" in content or "sea" in content:
            context_counter["ocean"] += 1
        if "city" in content or "street" in content:
            context_counter["city"] += 1

    triggers = [
        {"trigger": t, "count": c} for t, c in trigger_counter.most_common(15)
    ]
    contexts = [
        {"context": k, "count": v} for k, v in context_counter.most_common(10)
    ]

    return {
        "label": "Traces of Frisson",
        "total_scanned": len(fragments),
        "trace_count": len(traces),
        "traces": traces,
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


def analyze_frisson(user_id: str) -> Dict[str, Any]:
    docs = list(
        db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    )
    return analyze_frisson_fragments(docs)
