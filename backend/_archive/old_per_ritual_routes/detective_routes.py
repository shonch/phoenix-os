from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.detective import (
    DetectiveCreate,
    DetectiveResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/detective", tags=["Detective"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_clue(entry: DetectiveCreate, user=Depends(get_current_user_id)):
    """
    Detective ingestion using the unified PhoenixTag-aware ingestion wrapper.
    """
    try:
        user_id = user["user_id"]

        # Build ingestion request
        req = FragmentLogRequest(
            module="detective",
            type="detective_clue",
            layer="emotional",

            title=f"Detective Clue — {entry.clue_type}",
            subject=f"{entry.location} / {entry.symbol}",

            content=entry.note,
            weather=entry.weather,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=[
                entry.clue_type,
                entry.location,
                entry.status,
                entry.symbol,
                "detective_clue",
            ],

            body=entry.note,

            extra={
                "clue_type": entry.clue_type,
                "location": entry.location,
                "status": entry.status,
                "symbol": entry.symbol,
                "note": entry.note,
                "weather": entry.weather,
            },

            source="detective_routes",
        )

        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[DetectiveResponse])
def list_clues(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of detective clues.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["emotional_fragments"].find({
                "type": "detective_clue",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=DetectiveResponse)
def get_clue(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single clue retrieval.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["emotional_fragments"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Clue not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

