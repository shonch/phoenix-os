# phoenix_portfolio/backend/schemas/emerge.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class EmergeCreate(BaseModel):
    rev_type: str          # identity, grief, pattern, longing, etc.
    trigger: str           # dream, phrase, memory, etc.
    reflection: Optional[str] = None
    weather: Optional[str] = None


class EmergeResponse(EmergeCreate):
    id: str
    subject: str
    tags: List[str]
    timestamp: datetime
    type: str              # "revelation"
    content: str
    source_system: str

