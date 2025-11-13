# backend/ai_engine.py

def interpret_emotion(fragment):
    tag = fragment.tag.lower()
    intensity = fragment.intensity

    if tag == "grief" and intensity >= 8:
        return "Phoenix acknowledges deep sorrow. Denial protocols may be required."
    elif tag == "awe" and intensity >= 7:
        return "Phoenix mirrors resonance. Frisson detected."
    elif tag == "fatigue" and intensity >= 6:
        return "Phoenix recommends ritual decompression and emotional bandwidth preservation."
    else:
        return f"Phoenix received fragment: {tag} ({intensity}). No action required."
