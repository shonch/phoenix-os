# phoenix_portfolio/backend/schemas/fragments.py

from typing import List, Optional
from pydantic import BaseModel


class Fragment(BaseModel):
    id: str
    collection: str

    type: Optional[str] = None

    title: Optional[str] = None
    subject: Optional[str] = None

    tags: List[str] = []

    timestamp: Optional[str] = None
    date: Optional[str] = None

    content: Optional[str] = None

    source: Optional[str] = None

