# backend/schemas/detective.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DetectiveClueCreate(BaseModel):
    clue_type: str        # e.g. body, dream, glitch, longing
    location: str         # e.g. memory, Phoenix folder, terminal
    status: str           # e.g. unresolved, echoing, integrated
    symbol: str           # e.g. song, scent, phrase, image
    note: Optional[str] = None
    weather: Optional[str] = None
    tags: List[str] = []

class DetectiveClueResponse(DetectiveClueCreate):
    id: str
    timestamp: datetime
    source: Optional[str] = "detective_routes"
