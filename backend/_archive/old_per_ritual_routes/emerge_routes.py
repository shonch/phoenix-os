from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.emerge import (
    EmergeCreate,
    EmergeResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/emerge", tags=["Emerge"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_revelation(entry: EmergeCreate, user=Depends(get_current_user_id)):
    """
    Emerge ingestion using the unified PhoenixTag-aware ingestion wrapper.
    Writes to the 'revelations' collection.
    """
    try:
        user_id = user["user_id"]

        req = FragmentLogRequest(
            module="emerge",
            type="revelation",
            layer="revelation",

            title=f"Revelation: {entry.rev_type}",
            subject=f"Trigger: {entry.trigger}",

            content=entry.reflection,
            weather=entry.weather,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=[
                entry.rev_type,
                entry.trigger,
                "emerge",
                "revelation",
            ],

            body=entry.reflection,

            extra={
                "rev_type": entry.rev_type,
                "trigger": entry.trigger,
                "reflection": entry.reflection,
                "weather": entry.weather,
            },

            source="emerge_routes",
        )

        # ⭐ Write to revelations instead of emotional_fragments
        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[EmergeResponse])
def list_revelations(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of revelations.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["revelations"].find({
                "type": "revelation",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=EmergeResponse)
def get_revelation(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single revelation retrieval.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["revelations"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Revelation not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

