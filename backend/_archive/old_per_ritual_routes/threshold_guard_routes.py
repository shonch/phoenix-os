from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.threshold_guard import (
    ThresholdGuardCreate,
    ThresholdGuardResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/threshold_guard", tags=["Threshold Guard"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_threshold_scan(entry: ThresholdGuardCreate, user=Depends(get_current_user_id)):
    """
    Threshold Guard ingestion using the unified PhoenixTag-aware ingestion wrapper.
    Writes to the 'thresholds' collection.
    """
    try:
        user_id = user["user_id"]

        anchor_normalized = entry.anchor.lower().replace(" ", "_")

        req = FragmentLogRequest(
            module="threshold_guard",
            type="threshold_scan",
            layer="threshold",

            title=f"Threshold Scan — {entry.threshold_type}",
            subject=f"Status: {entry.status}",

            content=None,
            weather=entry.weather,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=[
                entry.threshold_type,
                entry.status,
                anchor_normalized,
                "threshold_scan",
            ],

            body=None,

            extra={
                "threshold_type": entry.threshold_type,
                "status": entry.status,
                "anchor": anchor_normalized,
                "weather": entry.weather,
            },

            source="threshold_guard_routes",
        )

        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[ThresholdGuardResponse])
def list_threshold_scans(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of threshold scans.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["thresholds"].find({
                "type": "threshold_scan",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=ThresholdGuardResponse)
def get_threshold_scan(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single threshold scan retrieval.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["thresholds"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Threshold scan not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

