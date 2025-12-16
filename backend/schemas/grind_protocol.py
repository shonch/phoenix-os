from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GrindScanCreate(BaseModel):
    energy: int
    sleep: str
    state: str
    urgency: str
    status: Optional[str] = None
    tags: List[str] = []

class GrindScanResponse(GrindScanCreate):
    id: str
    timestamp: datetime
    source: Optional[str] = "grind_protocol_routes"
