# phoenix_portfolio/backend/schemas/api_fragments.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Tag(BaseModel):
    tag_id: Optional[str] = None     # Phoenix UUID
    name: str                        # Human-facing name
    label: Optional[str] = None
    emoji: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    archetype: Optional[str] = None
    visibility: Optional[str] = None
    user_id: Optional[str] = None
    color: Optional[str] = None
    emotional_weight: Optional[float] = None


class FragmentLogRequest(BaseModel):
    module: str
    layer: str
    type: str

    title: Optional[str] = None
    subject: Optional[str] = None
    raw_text: str
    body: str

    # NOW full tag objects
    tags: List[Tag]

    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    version: str = "phoenixos.v1"


class FragmentResponse(BaseModel):
    id: str

    module: str
    layer: str
    type: str

    title: Optional[str] = None
    subject: Optional[str] = None
    raw_text: Optional[str] = None
    body: str

    # Full PhoenixTag objects returned
    tags: List[Tag]

    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    version: str = "phoenixos.v1"

