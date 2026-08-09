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
    PhoenixOS v3.0 Ritual Classifier
    Scores all ritual types by keyword-root hit count in the opening
    response text, picks the highest-scoring type. Ties break by a fixed
    priority order. `emotion` now requires real keyword signal too, instead
    of being the silent default whenever nothing else matches — it's only
    used as a true fallback when there's no opening text, or literally
    zero keyword hits across every category.
    """

    fragment = payload.get("fragment", {}) or {}
    metadata = fragment.get("metadata", {}) or {}

    raw_inputs = metadata.get("raw_inputs", []) or []
    threshold_type = (metadata.get("threshold_type") or "").lower().strip()

    opening_text = ""
    if raw_inputs:
        opening_text = (raw_inputs[0].get("text") or "").lower().replace("\n", " ").strip()

    # Threshold's explicit metadata flag still wins outright — it's a direct
    # signal from the ritual itself, not a keyword guess.
    if threshold_type in ("release", "initiation", "threshold", "transition"):
        return "threshold"

    keyword_map = {
        "threshold": [
            "stuck", "between", "crossroad", "choice", "choos", "decid",
            "path", "torn", "transition", "liminal", "shift", "edge",
            "threshold"
        ],
        "emerge": [
            "emerg", "rising", "surfac", "forming", "coming together",
            "coming into focus", "taking shape", "unfolding", "becoming clear"
        ],
        "pulse": [
            "quick", "brief", "checking in", "pulse", "heartbeat", "signal"
        ],
        "mirror": [
            "reflect", "who am i", "identit", "distort", "myself",
            "self-image", "contradict"
        ],
        "grind": [
            "grind", "exhaust", "burn", "burnout", "push", "friction",
            "resist", "wear", "tire", "strain"
        ],
        "anti_grind": [
            "relief", "reliev", "release", "easy", "rest", "light",
            "unburden", "at ease", "calm"
        ],
        "detective": [
            "clue", "pattern", "investigat", "mystery", "puzzle",
            "figure out", "connect the dots", "recur"
        ],
        "emotion": [
            "feel", "feeling", "emotion", "sad", "happy", "angry",
            "scared", "hurt", "joy", "grief", "lonely", "love",
            "anxious", "overwhelm"
        ],
    }

    if not opening_text:
        return "emotion"

    scores = {}
    for ritual_type, keywords in keyword_map.items():
        count = sum(1 for root in keywords if re.search(re.escape(root) + r"\w*", opening_text))
        if count > 0:
            scores[ritual_type] = count

    if not scores:
        return "emotion"

    priority_order = ["threshold", "emerge", "pulse", "mirror", "grind",
                       "anti_grind", "detective", "emotion"]
    best = max(scores.items(), key=lambda kv: (kv[1], -priority_order.index(kv[0])))
    return best[0]
