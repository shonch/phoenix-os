from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

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
#   FRISSON ENGINE — Resonance, Awe, Mythic Charge
# ============================================================

def analyze_frisson_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    """
    Frisson Engine (Phoenix v3)
    - ingestion-aware
    - PhoenixTag-aware
    - detects intensity, triggers, contexts
    - returns structured resonance profile
    """

    if not fragments:
        return {
            "summary": "⚡ No frisson traces found. This may be a quiet or flat phase.",
            "intensity_profile": [],
            "triggers": [],
            "contexts": [],
            "clues": [],
        }

    intensity_counter = Counter()
    trigger_counter = Counter()
    context_counter = Counter()

    for frag in fragments:
        content = (frag.get("content") or "").lower()
        tags = _extract_tags(frag)
        source = (frag.get("source") or "").lower()
        ctx = (frag.get("context") or frag.get("note") or "").lower()

        # -----------------------------
        # Intensity (if present)
        # -----------------------------
        intensity = frag.get("intensity")
        if isinstance(intensity, (int, float)):
            bucket = _bucket_intensity(intensity)
            intensity_counter[bucket] += 1

        # -----------------------------
        # Trigger detection — tags
        # -----------------------------
        for t in tags:
            if t in FRISSON_TAG_HINTS:
                trigger_counter[t] += 1

        # -----------------------------
        # Trigger detection — phrases
        # -----------------------------
        for phrase in FRISSON_PHRASES:
            if phrase in content:
                trigger_counter[phrase] += 1

        # -----------------------------
        # Context detection
        # -----------------------------
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

    # -----------------------------
    # Build outputs
    # -----------------------------
    intensity_profile = [
        {"bucket": b, "count": c} for b, c in sorted(intensity_counter.items())
    ]
    triggers = [
        {"trigger": t, "count": c} for t, c in trigger_counter.most_common(15)
    ]
    contexts = [
        {"context": k, "count": v} for k, v in context_counter.most_common(10)
    ]

    clues = _build_clues(intensity_profile, triggers, contexts)
    summary = _build_summary(intensity_profile, triggers, contexts)

    return {
        "summary": summary,
        "intensity_profile": intensity_profile,
        "triggers": triggers,
        "contexts": contexts,
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
                    # Continue list handling
            else:
                tags.append(str(t))

    # Case 3: single string
    elif isinstance(raw, str):
        tags.append(raw)

    # Always return a list
    return [t.lower() for t in tags if t]


def _bucket_intensity(value: float) -> str:
    """
    Convert numeric intensity into human-readable buckets.
    """
    if value >= 8:
        return "peak"
    if value >= 5:
        return "strong"
    if value >= 3:
        return "moderate"
    return "subtle"


def _build_clues(
    intensity_profile: List[Dict[str, Any]],
    triggers: List[Dict[str, Any]],
    contexts: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build frisson clues from intensity, triggers, and contexts.
    """

    clues = []

    # Intensity clues
    for item in intensity_profile:
        clues.append({
            "type": "intensity",
            "bucket": item["bucket"],
            "count": item["count"],
        })

    # Trigger clues
    for trig in triggers:
        clues.append({
            "type": "trigger",
            "trigger": trig["trigger"],
            "count": trig["count"],
        })

    # Context clues
    for ctx in contexts:
        clues.append({
            "type": "context",
            "context": ctx["context"],
            "count": ctx["count"],
        })

    return clues


def _build_summary(
    intensity_profile: List[Dict[str, Any]],
    triggers: List[Dict[str, Any]],
    contexts: List[Dict[str, Any]],
) -> str:
    """
    Build a human-readable summary of frisson activity.
    """

    parts = []

    if intensity_profile:
        parts.append(f"⚡ {len(intensity_profile)} intensity signals")

    if triggers:
        parts.append(f"🎯 {len(triggers)} triggers detected")

    if contexts:
        parts.append(f"🌍 {len(contexts)} contexts involved")

    if not parts:
        return "⚡ No frisson traces found."

    return " | ".join(parts)

from phoenix_portfolio.backend.mongo_client import db

def analyze_frisson(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_frisson_fragments.
    Loads emotional_fragments for this user and filters for frisson-related ones.
    """
    # Load emotional fragments (frisson is a subset of emotional resonance)
    docs = list(
        db["emotional_fragments"]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
    )

    # Filter for fragments that contain frisson hints
    frisson_docs = []
    for d in docs:
        content = (d.get("content") or "").lower()
        tags = d.get("tags", [])
        tag_list = []

        # Normalize tags
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

        # Check for frisson signals
        if any(hint in content for hint in FRISSON_TAG_HINTS) or any(
            hint in tag_list for hint in FRISSON_TAG_HINTS
        ):
            frisson_docs.append(d)

    return analyze_frisson_fragments(frisson_docs)

