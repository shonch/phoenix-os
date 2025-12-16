from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AntiGrindCreate(BaseModel):
    signal: str
    action: str
    weather: Optional[str] = None
    tags: List[str] = []

class AntiGrindResponse(AntiGrindCreate):
    id: str
    timestamp: datetime
    source: Optional[str] = "anti_grind_routes"
