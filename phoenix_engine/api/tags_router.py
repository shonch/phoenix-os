# phoenix_engine/api/tags_router.py

from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from phoenix_engine.api.main import verify_token
from phoenix_engine.models.tag import PhoenixTag

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "phoenix_engine")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

router = APIRouter(prefix="/tags", tags=["tags"])


def normalize_label(name: str) -> str:
    """
    Convert raw name into normalized machine label.
    """
    return (
        name.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


@router.post("/")
def create_tag(tag: PhoenixTag, caller_user_id: str = Depends(verify_token)):
    """
    Create a PhoenixTag using the unified schema.
    Ensures:
      - user identity matches token
      - label is normalized
      - full PhoenixTag object is stored
    """

    # Enforce identity
    if tag.user_id != caller_user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create tags for a different user"
        )

    # Normalize label
    normalized = normalize_label(tag.name)
    tag.label = normalized

    # Check for existing tag
    existing = db.symbolic_tags.find_one({
        "label": tag.label,
        "user_id": tag.user_id
    })

    if existing:
        # Return existing tag as PhoenixTag
        return PhoenixTag(**existing)

    # Insert new tag
    tag_dict = tag.dict()
    result = db.symbolic_tags.insert_one(tag_dict)

    # Attach MongoDB ID to returned object
    tag_dict["_id"] = str(result.inserted_id)

    return tag_dict

