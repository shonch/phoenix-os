from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc

Fragment = Dict[str, Any]

EMOTION_TAGS = {
    "joy", "sadness", "anger", "fear", "shame", "guilt",
    "hope", "calm", "peace", "anxiety", "overwhelm",
    "clarity", "fog", "drift", "stability", "exhaustion",
    "tension", "release", "relief", "confusion",
}

EMOTION_PHRASES = [
    "i feel", "i'm feeling", "im feeling", "emotionally", "it feels like",
    "i'm overwhelmed", "im overwhelmed", "i'm exhausted", "im exhausted",
    "i'm anxious", "im anxious",
    "i feel clear", "i feel foggy", "i feel lost",
    "i feel grounded", "i feel steady",
]

# ============================================================
#   EMOTION ENGINE — Emotional Weather, Cycles, Dominants
# ============================================================

def analyze_emotion_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    """
    Emotion Engine (Phoenix v3)
    - ingestion-aware
    - PhoenixTag-aware
    - detects emotional tones, weather patterns, cycles
    """

    if not fragments:
        return {
            "summary": "🌤️ Emotional weather is quiet — no strong signals detected.",
            "dominant_emotions": [],
            "weather_patterns": [],
            "cycles": [],
            "clues": [],
        }

    emotion_counter = Counter()
    weather_counter = Counter()
    by_day = Counter()

    for frag in fragments:
        content = (frag.get("content") or "").lower()
        tags = _extract_tags(frag)
        ts = _extract_timestamp(frag)

        # Tag-based emotion detection
        for t in tags:
            if t in EMOTION_TAGS:
                emotion_counter[t] += 1

        # Phrase-based emotion detection
        for phrase in EMOTION_PHRASES:
            if phrase in content:
                weather_counter[phrase] += 1

        # Cycles (by day)
        if ts:
            by_day[ts.date()] += 1

    # Build outputs
    dominant_emotions = [
        {"emotion": e, "count": c} for e, c in emotion_counter.most_common(10)
    ]
    weather_patterns = [
        {"pattern": p, "count": c} for p, c in weather_counter.most_common(10)
    ]
    cycles = [
        {"day": d.isoformat(), "count": c}
        for d, c in sorted(by_day.items())
    ]

    clues = _build_clues(dominant_emotions, weather_patterns, cycles)
    summary = _build_summary(dominant_emotions, weather_patterns, cycles)

    return {
        "summary": summary,
        "dominant_emotions": dominant_emotions,
        "weather_patterns": weather_patterns,
        "cycles": cycles,
        "clues": clues,
    }

# ============================================================
#   HELPERS
# ============================================================

def _extract_tags(frag: Fragment) -> List[str]:
    """Normalize tags from multiple Phoenix ingestion formats."""
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
    """Normalize timestamps from multiple Phoenix formats."""
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
#   CLUE + SUMMARY BUILDERS
# ============================================================

def _build_clues(dominant, weather, cycles) -> List[str]:
    """Generate simple interpretive clues from emotional signals."""
    clues = []

    if dominant:
        top = dominant[0]["emotion"]
        clues.append(f"Dominant emotional tone: {top}")

    if weather:
        top_weather = weather[0]["pattern"]
        clues.append(f"Frequent emotional expression: '{top_weather}'")

    if cycles:
        most_active = max(cycles, key=lambda x: x["count"])
        clues.append(f"Most emotionally active day: {most_active['day']}")

    if not clues:
        clues.append("Emotional signals are subtle or diffuse.")

    return clues


def _build_summary(dominant, weather, cycles) -> str:
    """Generate a human-readable emotional weather summary."""
    if not dominant and not weather:
        return "🌤️ Emotional weather is quiet — no strong signals detected."

    parts = []

    if dominant:
        parts.append(f"Dominant emotion: {dominant[0]['emotion']}")

    if weather:
        parts.append(f"Common expression: '{weather[0]['pattern']}'")

    if cycles:
        most_active = max(cycles, key=lambda x: x["count"])
        parts.append(f"Peak emotional activity on {most_active['day']}")

    return " | ".join(parts)

# ============================================================
#   STATE ENGINE WRAPPER
# ============================================================

def analyze_emotion(user_id: str) -> Dict[str, Any]:
    """
    State-engine compatible wrapper:
    - loads emotional_fragments for a user
    - delegates to analyze_emotion_fragments
    """
    fragments = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    ]
    return analyze_emotion_fragments(fragments)

