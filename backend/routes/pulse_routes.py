from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.pulse import (
    PulseFragmentCreate,
    PulseFragmentResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/pulse", tags=["Pulse"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_pulse(entry: PulseFragmentCreate, user=Depends(get_current_user_id)):
    """
    Pulse ingestion using the unified PhoenixTag-aware ingestion wrapper.
    """
    try:
        user_id = user["user_id"]

        # Build ingestion request
        req = FragmentLogRequest(
            module="pulse",
            type="pulse_fragment",
            layer="emotional",

            title=entry.title,
            subject=f"Emotion: {entry.emotion}",

            content=entry.fragment,
            weather=None,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=(entry.tags or []) + ["pulse"],

            body=entry.fragment,

            extra={
                "title": entry.title,
                "emotion": entry.emotion,
                "fragment": entry.fragment,
            },

            source="pulse_routes",
        )

        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[PulseFragmentResponse])
def list_pulses(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of pulse fragments.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["emotional_fragments"].find({
                "type": "pulse_fragment",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=PulseFragmentResponse)
def get_pulse(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single pulse retrieval.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["emotional_fragments"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Pulse fragment not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

