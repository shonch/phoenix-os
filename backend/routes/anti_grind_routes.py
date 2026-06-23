from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.anti_grind import (
    AntiGrindCreate,
    AntiGrindResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/anti_grind", tags=["Anti-Grind"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_override(entry: AntiGrindCreate, user=Depends(get_current_user_id)):
    """
    Anti-Grind ingestion using the unified PhoenixTag-aware ingestion wrapper.
    """
    try:
        user_id = user["user_id"]

        # Build ingestion request
        req = FragmentLogRequest(
            module="anti_grind",
            type="grind_override",
            layer="emotional",

            title="Anti-Grind Override",
            subject=f"Signal: {entry.signal}",

            content=entry.note if hasattr(entry, "note") else None,
            weather=entry.weather,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=(entry.tags or []) + ["grind_override"],

            body=entry.note if hasattr(entry, "note") else None,

            extra={
                "signal": entry.signal,
                "action": entry.action,
                "weather": entry.weather,
                "note": getattr(entry, "note", None),
            },

            source="anti_grind_routes",
        )

        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[AntiGrindResponse])
def list_overrides(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of anti-grind overrides.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["emotional_fragments"].find({
                "type": "grind_override",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=AntiGrindResponse)
def get_override(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single override retrieval.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["emotional_fragments"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Override not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

