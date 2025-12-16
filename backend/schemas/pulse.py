# backend/schemas/pulse.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PulseFragmentCreate(BaseModel):
    title: str
    emotion: str
    tags: List[str]
    fragment: str

class PulseFragmentResponse(BaseModel):
    id: str
    title: str
    emotion: str
    tags: List[str]
    fragment: str
    timestamp: datetime
    source: Optional[str] = "pulse_routes"
