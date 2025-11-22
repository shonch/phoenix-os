# phoenix_engine/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: EmailStr
    password_hash: str
    roles: List[str] = ["user"]
    created_at: Optional[datetime] = None
    note: Optional[str] = None
