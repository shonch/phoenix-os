# phoenix_engine/models/emotion.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmotionFragment(BaseModel):
    user_id: str                # link fragment to a user
    tag: str                    # e.g. "grief", "awe", "resonance"
    intensity: int              # scale 1–10
    timestamp: datetime         # ISO timestamp
    notes: Optional[str] = None # poetic reflection, emotional context
