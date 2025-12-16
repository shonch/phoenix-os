from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ThresholdCreate(BaseModel):
    threshold_type: str
    status: str
    anchor: str
    weather: Optional[str] = None
    tags: List[str] = ["threshold"]

class ThresholdResponse(ThresholdCreate):
    id: str
    date: datetime
    subject: str
    content: str
    source: Optional[str] = "threshold_guard_routes"
