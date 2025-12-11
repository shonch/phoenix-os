# backend/schemas/emotion.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 🌱 Core emotional fragment — the heartbeat of Phoenix
class EmotionFragment(BaseModel):
    tag: str = Field(..., example="awe")
    intensity: int = Field(..., ge=1, le=10, example=7)
    timestamp: datetime = Field(..., example="2025-12-05T08:36:00Z")
    notes: Optional[str] = Field(None, example="The wind moved the spruce lights gently.")

# 🌌 Log entry — the vessel that carries fragments
class EmotionLogCreate(BaseModel):
    subject: str = Field(..., example="Morning ritual walk")
    tags: List[str] = Field(..., example=["ritual", "nature", "resonance"])
    weather: Optional[str] = Field(None, example="lucid")
    content: Optional[str] = Field(None, example="Markdown notes or poetic reflection.")
    fragments: Optional[List[EmotionFragment]] = None  # embed one or more fragments

# 📜 Response — the archive returned to the user
class EmotionLogResponse(EmotionLogCreate):
    id: str
    user_id: str
    timestamp: datetime
    updated_at: Optional[datetime] = None
