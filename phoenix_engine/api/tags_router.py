# phoenix_engine/api/tags_router.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from phoenix_engine.api.main import verify_token  # import the JWT verifier

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "phoenix_engine")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

router = APIRouter(prefix="/tags", tags=["tags"])

class TagCreate(BaseModel):
    tag_name: str
    user_id: str
    emoji: str = "🌀"
    category: str = "custom"
    description: str = ""
    archetype: str = "emergent"
    visibility: str = "private"

@router.post("/")
def create_tag(tag: TagCreate, caller_user_id: str = Depends(verify_token)):
    # Optional: enforce that the caller creates tags only for themselves
    if tag.user_id != caller_user_id:
        raise HTTPException(status_code=403, detail="Cannot create tags for a different user")

    existing = db.symbolic_tags.find_one({"label": tag.tag_name, "user_id": tag.user_id})
    if existing:
        return {"tag_id": str(existing["_id"]), "status": "exists"}

    new_tag = {
        "label": tag.tag_name,
        "user_id": tag.user_id,
        "emoji": tag.emoji,
        "category": tag.category,
        "description": tag.description,
        "archetype": tag.archetype,
        "visibility": tag.visibility,
        "times_used": 1,
        "promoted": False,
    }
    result = db.symbolic_tags.insert_one(new_tag)
    return {"tag_id": str(result.inserted_id), "status": "created"}

@router.get("/")
def list_tags(caller_user_id: str = Depends(verify_token)):
    tags = list(db.symbolic_tags.find({"user_id": caller_user_id}))
    for tag in tags:
        tag["_id"] = str(tag["_id"])  # make ObjectId JSON‑friendly
    return tags
