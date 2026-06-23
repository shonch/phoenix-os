from typing import List, Dict, Any

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

# Canonical classifier buckets
TYPE_KEYS = [
    "emotion_log",
    "frisson",
    "grief",
    "grind",
    "detective",
    "mirror",
    "threshold",
    "emerge",
    "ritual",
    "mythic",
    "console",
    "system",
    "code_ritual",
    "dream",
    "unknown",
]

# Mapping from ingestion wrapper types → classifier buckets
INGESTION_TYPE_MAP = {
    "grind_scan": "grind",
    "grind_override": "grind",
    "detective_clue": "detective",
    "revelation": "mirror",
    "threshold_scan": "threshold",
    "pulse_fragment": "emotion_log",
    "emotion_log": "emotion_log",
    "frisson_trace": "frisson",
    "grief_archive": "grief",
}

# Emerge uses revelations collection but is semantically distinct
COLLECTION_TYPE_MAP = {
    "revelations": "emerge",
    "thresholds": "threshold",
    "clues": "detective",
}


def _lower(s: Any) -> str:
    return str(s).lower() if isinstance(s, str) else ""


def infer_type_from_explicit_fields(doc: dict) -> str | None:
    raw = doc.get("type")
    if raw:
        t = _lower(raw)
        if t in INGESTION_TYPE_MAP:
            return INGESTION_TYPE_MAP[t]
    return None


def infer_type_from_collection(collection_name: str) -> str | None:
    return COLLECTION_TYPE_MAP.get(collection_name)


def infer_type_from_tags(doc: dict) -> str | None:
    tags = doc.get("tags", [])
    if isinstance(tags, dict):
        tags = [tags.get("tag_name", "")]
    if not isinstance(tags, list):
        return None

    joined = _lower(" ".join(str(t) for t in tags))

    if "grind" in joined:
        return "grind"
    if "detective" in joined or "clue" in joined:
        return "detective"
    if "threshold" in joined:
        return "threshold"
    if "revelation" in joined or "mirror" in joined:
        return "mirror"
    if "emerge" in joined:
        return "emerge"
    if "frisson" in joined:
        return "frisson"
    if "grief" in joined:
        return "grief"
    if "emotion" in joined:
        return "emotion_log"

    return None


def infer_type_for_doc(doc: dict, collection_name: str) -> str:
    t = infer_type_from_explicit_fields(doc)
    if t:
        return t

    t = infer_type_from_collection(collection_name)
    if t:
        return t

    t = infer_type_from_tags(doc)
    if t:
        return t

    return "unknown"


def classify_fragments(
    emotional_fragments: List[dict],
    legacy_fragments: List[dict],
    revelations: List[dict],
    thresholds: List[dict],
    clues: List[dict],
) -> Dict[str, List[dict]]:

    buckets: Dict[str, List[dict]] = {k: [] for k in TYPE_KEYS}

    def add_docs(docs: List[dict], collection_name: str):
        for doc in docs:
            t = infer_type_for_doc(doc, collection_name)
            if t not in buckets:
                t = "unknown"
            buckets[t].append(doc)

    add_docs(emotional_fragments, "emotional_fragments")
    add_docs(legacy_fragments, "fragments")
    add_docs(revelations, "revelations")
    add_docs(thresholds, "thresholds")
    add_docs(clues, "clues")

    return buckets


def analyze_classifiers(user_id: str) -> Dict[str, List[dict]]:
    """
    State-engine wrapper for classify_fragments.
    Loads all fragment collections for this user and returns classifier buckets.
    """

    emotional = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    legacy = [
        serialize_doc(d)
        for d in db["fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    revelations = [
        serialize_doc(d)
        for d in db["revelations"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    thresholds = [
        serialize_doc(d)
        for d in db["thresholds"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    clues = [
        serialize_doc(d)
        for d in db["clues"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]

    return classify_fragments(
        emotional_fragments=emotional,
        legacy_fragments=legacy,
        revelations=revelations,
        thresholds=thresholds,
        clues=clues,
    )

