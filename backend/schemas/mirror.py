# phoenix_portfolio/backend/schemas/mirror.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MirrorCreate(BaseModel):
    note: Optional[str] = None
    weather: Optional[str] = None


class MirrorResponse(MirrorCreate):
    id: str
    tags: List[str]
    theme: str
    timestamp: datetime
    type: str
    content: str
    source_system: str

