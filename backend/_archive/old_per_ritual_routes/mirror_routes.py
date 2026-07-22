from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.mirror import (
    MirrorCreate,
    MirrorResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/mirror", tags=["Mirror"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_reflection(entry: MirrorCreate, user=Depends(get_current_user_id)):
    """
    Mirror ingestion using the unified PhoenixTag-aware ingestion wrapper.
    """
    try:
        user_id = user["user_id"]

        req = FragmentLogRequest(
            module="mirror",
            type="revelation",
            layer="revelation",

            title="Mirror Reflection",
            subject="Identity / Mythic Self",

            content=entry.note,
            weather=entry.weather,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=[
                "mirror",
                "revelation",
                "mythic_identity",
            ],

            body=entry.note,

            extra={
                "theme": "Mirror reflection",
                "note": entry.note,
                "weather": entry.weather,
            },

            source="mirror_routes",
        )

        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[MirrorResponse])
def list_reflections(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of mirror reflections.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["emotional_fragments"].find({
                "type": "revelation",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=MirrorResponse)
def get_reflection(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single reflection retrieval.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["emotional_fragments"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Reflection not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

