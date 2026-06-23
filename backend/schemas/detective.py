# phoenix_portfolio/backend/schemas/detective.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DetectiveCreate(BaseModel):
    clue_type: str        # e.g. body, dream, glitch, longing
    location: str         # e.g. memory, Phoenix folder, terminal, dream
    status: str           # e.g. unresolved, echoing, integrated
    symbol: str           # e.g. song, scent, phrase, image
    note: Optional[str] = None
    weather: Optional[str] = None

class DetectiveResponse(DetectiveCreate):
    id: str
    tags: List[str]
    timestamp: datetime
    type: str
    content: str
    source_system: str

