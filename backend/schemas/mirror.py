from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MirrorCreate(BaseModel):
    tags: List[str] = ["mirror", "revelation", "mythic_identity"]

class MirrorResponse(MirrorCreate):
    id: str
    timestamp: datetime
    theme: str = "Mirror reflection"
    note: str = "Reflected on mythic identity. Reclaimed emotional truth."
    content: str
    source: Optional[str] = "mirror_routes"
