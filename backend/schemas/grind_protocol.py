# phoenix_portfolio/backend/schemas/grind_protocol.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GrindScanCreate(BaseModel):
    energy: int                  # 1–10
    sleep: str                   # poor, okay, deep
    state: str                   # foggy, anxious, numb, tender, etc.
    urgency: str                 # yes / no
    note: Optional[str] = None   # optional reflection
    weather: Optional[str] = None  # optional emotional weather


class GrindScanResponse(GrindScanCreate):
    id: str
    status: str                  # pause / clear
    tags: List[str]
    timestamp: datetime
    type: str                    # "grind_scan"
    content: str                 # markdown
    source_system: str           # "grind_protocol_routes"

