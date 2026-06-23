# phoenix_portfolio/backend/services/classifier.py

"""
PhoenixOS Ritual Classifier

This classifier inspects the raw payload and determines which ritual
builder should be invoked. It returns a string that matches the keys
in ritual_map.
"""

def classify_ritual_type(payload: dict) -> str:
    """
    Determine ritual type based on the presence of key fields.
    This is a simple rule-based classifier for PhoenixOS v1.

    The classifier returns one of:
    - "pulse"
    - "emotion"
    - "grind"
    - "anti_grind"
    - "detective"
    - "mirror"
    - "emerge"
    - "threshold"
    """

    # 1. Pulse
    if payload.get("raw_fragment") and payload.get("emotion"):
        return "pulse"

    # 2. Emotion
    if payload.get("emotion") and payload.get("body"):
        return "emotion"

    # 3. Grind
    if payload.get("task") or payload.get("resistance"):
        return "grind"

    # 4. Anti-Grind
    if payload.get("relief") or payload.get("cause"):
        return "anti_grind"

    # 5. Detective
    if payload.get("clue") or payload.get("insight"):
        return "detective"

    # 6. Mirror
    if payload.get("reflection") or payload.get("distortion"):
        return "mirror"

    # 7. Emerge
    if payload.get("breakthrough") or payload.get("context"):
        return "emerge"

    # 8. Threshold
    if payload.get("boundary") or payload.get("violation"):
        return "threshold"

    # Default fallback
    return "emotion"

