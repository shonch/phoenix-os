from pydantic import BaseModel

class EmotionFragment(BaseModel):
    tag: str           # e.g. "grief", "awe", "resonance"
    intensity: int     # scale from 1–10
    timestamp: str     # ISO format or custom ritual time
    notes: str         # poetic reflection, emotional context
