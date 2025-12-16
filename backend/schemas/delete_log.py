from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeleteLogCreate(BaseModel):
    fragment_id: str
    fragment_type: str
    reason: Optional[str] = None

class DeleteLogResponse(BaseModel):
    id: str
    fragment_id: str
    fragment_type: str
    reason: Optional[str]
    timestamp: datetime
    user_id: str
