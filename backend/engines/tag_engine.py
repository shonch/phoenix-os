# phoenix_portfolio/backend/engines/tag_engine.py

from collections import Counter, defaultdict
from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

Fragment = Dict[str, Any]

ARCHETYPE_HINTS = {
    "hero", "shadow", "mentor", "threshold", "journey",
    "loss", "rebirth", "anchor", "ritual", "identity",
    "wanderer", "seer", "guardian", "child", "warrior",
    "sage", "creator", "destroyer", "lover", "orphan",
}


# ============================================================
#   TAG ENGINE — counts and co-occurrence only
# ============================================================

def analyze_tag_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    if not fragments:
        return {
            "tag_frequency": [],
            "archetypes": [],
            "co_occurrence": [],
        }

    tag_counter = Counter()
    archetype_counter = Counter()
    co_occurrence_map = defaultdict(Counter)

    for frag in fragments:
        tags = _extract_tags(frag)

        for t in tags:
            tag_counter[t] += 1

        for t in tags:
            if t in ARCHETYPE_HINTS:
                archetype_counter[t] += 1

        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                co_occurrence_map[t1][t2] += 1
                co_occurrence_map[t2][t1] += 1

    tag_frequency = [
        {"tag": t, "count": c} for t, c in tag_counter.most_common(25)
    ]

    archetypes = [
        {"archetype": t, "count": c}
        for t, c in archetype_counter.most_common(15)
    ]

    co_occurrence = _flatten_co_occurrence(co_occurrence_map)

    return {
        "tag_frequency": tag_frequency,
        "archetypes": archetypes,
        "co_occurrence": co_occurrence,
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


def _flatten_co_occurrence(co_map):
    pairs = []
    for t1, inner in co_map.items():
        for t2, count in inner.items():
            if count > 1:
                pairs.append({"pair": (t1, t2), "count": count})
    return sorted(pairs, key=lambda x: -x["count"])[:25]


def analyze_tags(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_tag_fragments.
    Loads from all relevant collections (legacy + current ritual
    pipeline), so old and new tag data both appear.
    """
    collections_to_scan = [
        "fragments", "emotional_fragments", "revelations", "thresholds", "clues"
    ]

    docs: List[dict] = []
    for coll_name in collections_to_scan:
        docs.extend(
            serialize_doc(d)
            for d in db[coll_name]
            .find({"user_id": user_id})
            .sort("timestamp", -1)
        )

    return analyze_tag_fragments(docs)
