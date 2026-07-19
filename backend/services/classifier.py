# phoenix_portfolio/backend/services/classifier.py

import re


def _matches_any(text: str, roots: list[str]) -> bool:
    """
    Match if any keyword root appears in the text, regardless of word
    ending (e.g. "exhaust" matches "exhausted", "exhausting", "exhaustion").
    """
    for root in roots:
        pattern = re.escape(root) + r"\w*"
        if re.search(pattern, text):
            return True
    return False


def classify_ritual_type(payload: dict) -> str:
    """
    PhoenixOS v2.5 Ritual Classifier
    All branches check actual response text (raw_inputs[0].text), not step
    labels. Keyword lists use word ROOTS matched via regex, so different
    conjugations/forms (exhaust/exhausted/exhausting/exhaustion) all match
    without needing every variant spelled out. Keyword lists are a first
    pass — tune freely during testing.
    """

    fragment = payload.get("fragment", {}) or {}
    metadata = fragment.get("metadata", {}) or {}

    raw_inputs = metadata.get("raw_inputs", []) or []
    threshold_type = (metadata.get("threshold_type") or "").lower().strip()

    opening_text = ""
    if raw_inputs:
        opening_text = (raw_inputs[0].get("text") or "").lower().replace("\n", " ").strip()

    # ---------------------------------------------------------
    # 1. THRESHOLD RITUAL (highest priority)
    # ---------------------------------------------------------
    threshold_keywords = [
        "stuck", "between", "crossroad", "choice", "choos", "decid",
        "path", "torn", "transition", "liminal", "shift", "edge",
        "threshold"
    ]

    if threshold_type in ("release", "initiation", "threshold", "transition"):
        return "threshold"

    if opening_text and _matches_any(opening_text, threshold_keywords):
        return "threshold"

    # ---------------------------------------------------------
    # 2. PULSE RITUAL
    # ---------------------------------------------------------
    pulse_keywords = [
        "quick", "brief", "checking in", "pulse", "heartbeat", "signal"
    ]

    if opening_text and _matches_any(opening_text, pulse_keywords):
        return "pulse"

    # ---------------------------------------------------------
    # 3. MIRROR RITUAL
    # ---------------------------------------------------------
    mirror_keywords = [
        "reflect", "who am i", "identit", "distort", "myself",
        "self-image", "contradict"
    ]

    if opening_text and _matches_any(opening_text, mirror_keywords):
        return "mirror"

    # ---------------------------------------------------------
    # 4. GRIND / ANTI-GRIND RITUAL
    # ---------------------------------------------------------
    grind_keywords = [
        "grind", "exhaust", "burn", "burnout", "push", "friction",
        "resist", "wear", "tire", "strain"
    ]
    anti_grind_keywords = [
        "relief", "reliev", "release", "easy", "rest", "light",
        "unburden", "at ease", "calm"
    ]

    if opening_text and _matches_any(opening_text, grind_keywords):
        return "grind"

    if opening_text and _matches_any(opening_text, anti_grind_keywords):
        return "anti_grind"

    # ---------------------------------------------------------
    # 5. DETECTIVE RITUAL
    # ---------------------------------------------------------
    detective_keywords = [
        "clue", "pattern", "investigat", "mystery", "puzzle",
        "figure out", "connect the dots", "recur"
    ]

    if opening_text and _matches_any(opening_text, detective_keywords):
        return "detective"

    # ---------------------------------------------------------
    # 6. DEFAULT
    # ---------------------------------------------------------
    return "emotion"
