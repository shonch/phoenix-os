# phoenix_portfolio/backend/schemas/threshold_guard.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ThresholdGuardCreate(BaseModel):
    threshold_type: str          # grief, fatigue, legacy, trust, etc.
    status: str                  # stable, fragile, breached
    anchor: str                  # word, symbol, or emotional tether
    weather: Optional[str] = None


class ThresholdGuardResponse(ThresholdGuardCreate):
    id: str
    subject: str
    tags: List[str]
    timestamp: datetime
    type: str                    # "threshold_scan"
    content: str
    source_system: str

