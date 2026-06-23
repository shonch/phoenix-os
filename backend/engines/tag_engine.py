from collections import Counter, defaultdict
from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

Fragment = Dict[str, Any]

# Tags that often carry symbolic or archetypal weight
ARCHETYPE_HINTS = {
    "hero", "shadow", "mentor", "threshold", "journey",
    "loss", "rebirth", "anchor", "ritual", "identity",
    "wanderer", "seer", "guardian", "child", "warrior",
    "sage", "creator", "destroyer", "lover", "orphan",
}


# ============================================================
#   TAG ENGINE — Symbolic Field, Archetypes, Constellations
# ============================================================

def analyze_tag_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    """
    Tag Engine (Phoenix v3)
    - ingestion-aware
    - PhoenixTag-aware
    - detects symbolic tag frequency
    - detects archetypal patterns
    - detects tag constellations (co-occurrence)
    """

    if not fragments:
        return {
            "summary": "🔖 No tag activity detected.",
            "tag_frequency": [],
            "archetypes": [],
            "co_occurrence": [],
            "clues": [],
        }

    tag_counter = Counter()
    archetype_counter = Counter()
    co_occurrence_map = defaultdict(Counter)

    # -------------------------
    # PASS 1 — Scan fragments
    # -------------------------
    for frag in fragments:
        tags = _extract_tags(frag)

        # frequency
        for t in tags:
            tag_counter[t] += 1

        # archetype detection
        for t in tags:
            if t in ARCHETYPE_HINTS:
                archetype_counter[t] += 1

        # co-occurrence detection
        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                co_occurrence_map[t1][t2] += 1
                co_occurrence_map[t2][t1] += 1

    # -------------------------
    # Build outputs
    # -------------------------
    tag_frequency = [
        {"tag": t, "count": c} for t, c in tag_counter.most_common(25)
    ]

    archetypes = [
        {"archetype": t, "count": c}
        for t, c in archetype_counter.most_common(15)
    ]

    co_occurrence = _flatten_co_occurrence(co_occurrence_map)

    clues = _build_clues(tag_frequency, archetypes, co_occurrence)
    summary = _build_summary(tag_frequency, archetypes, co_occurrence)

    return {
        "summary": summary,
        "tag_frequency": tag_frequency,
        "archetypes": archetypes,
        "co_occurrence": co_occurrence,
        "clues": clues,
    }


# ============================================================
#   HELPERS
# ============================================================

def _extract_tags(frag: Fragment) -> List[str]:
    """
    Normalize tags:
    - strings
    - PhoenixTag objects
    - mixed lists
    """
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


def _flatten_co_occurrence(co_map):
    pairs = []
    for t1, inner in co_map.items():
        for t2, count in inner.items():
            if count > 1:
                pairs.append({"pair": (t1, t2), "count": count})
    return sorted(pairs, key=lambda x: -x["count"])[:25]


def _build_clues(tag_frequency, archetypes, co_occurrence) -> List[str]:
    clues = []

    if tag_frequency:
        top = ", ".join(t["tag"] for t in tag_frequency[:5])
        clues.append(f"Most active tags: {top}.")

    if archetypes:
        top_a = ", ".join(a["archetype"] for a in archetypes[:5])
        clues.append(f"Archetypal signals detected: {top_a}.")

    if co_occurrence:
        t1, t2 = co_occurrence[0]["pair"]
        clues.append(f"Strong tag constellation detected: {t1} ↔ {t2}.")

    if not clues:
        clues.append("Tag activity is subtle — symbolic field is quiet.")

    return clues


def _build_summary(tag_frequency, archetypes, co_occurrence) -> str:
    parts = []

    if not tag_frequency:
        return "🔖 Tag field is quiet."

    parts.append("🔖 Tag activity detected.")

    if archetypes:
        parts.append("• Archetypal patterns emerging.")

    if co_occurrence:
        parts.append("• Tag constellations forming.")

    return "\n".join(parts)


def analyze_tags(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_tag_fragments.
    Loads fragments for this user and passes them into the Tag Engine.
    """
    # Load all fragments for this user, serialized
    docs = [
        serialize_doc(d)
        for d in db["fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    return analyze_tag_fragments(docs)

