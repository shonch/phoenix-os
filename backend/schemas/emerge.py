from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EmergeCreate(BaseModel):
    rev_type: str
    trigger: str
    reflection: Optional[str] = None
    weather: Optional[str] = None
    tags: List[str] = ["emerge"]

class EmergeResponse(EmergeCreate):
    id: str
    date: datetime
    subject: str
    content: str
    source: Optional[str] = "emerge_routes"
