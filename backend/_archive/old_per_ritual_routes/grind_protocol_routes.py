from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from phoenix_portfolio.backend.schemas.grind_protocol import (
    GrindScanCreate,
    GrindScanResponse,
)
from phoenix_portfolio.backend.schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/grind", tags=["Grind Protocol"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


def infer_status(energy: int, sleep: str, urgency: str) -> str:
    if energy <= 4:
        return "pause"
    if sleep == "poor":
        return "pause"
    if urgency == "yes":
        return "pause"
    return "clear"


@router.post("/", response_model=FragmentResponse)
def log_scan(entry: GrindScanCreate, user=Depends(get_current_user_id)):
    """
    Grind Protocol ingestion using the unified PhoenixTag-aware ingestion wrapper.
    """
    try:
        user_id = user["user_id"]
        status = infer_status(entry.energy, entry.sleep, entry.urgency)

        # Build the ingestion request
        req = FragmentLogRequest(
            module="grind_protocol",
            type="grind_scan",
            layer="emotional",

            # Grind protocol does not use title/subject; note becomes content
            title=f"Grind Scan ({status})",
            subject=f"Energy {entry.energy}, Sleep {entry.sleep}",

            content=entry.note,
            weather=entry.weather,

            # Tags become PhoenixTag objects via ingestion wrapper
            tags=[entry.state, entry.sleep, status, "grind_scan"],

            # Body is optional but helps expressive grammar
            body=entry.note,

            # Module-specific payload
            extra={
                "energy": entry.energy,
                "sleep": entry.sleep,
                "state": entry.state,
                "urgency": entry.urgency,
                "status": status,
                "weather": entry.weather,
            },

            source="grind_protocol_routes",
        )

        return ingest_fragment(req, user_id=user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[GrindScanResponse])
def list_scans(user=Depends(get_current_user_id)):
    """
    Legacy-compatible listing of grind scans.
    """
    try:
        from phoenix_portfolio.backend.mongo_client import db
        docs = list(
            db["emotional_fragments"].find({
                "type": "grind_scan",
                "user_id": user["user_id"],
            })
        )
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=GrindScanResponse)
def get_scan(id: str, user=Depends(get_current_user_id)):
    """
    Legacy-compatible single scan retrieval.
    """
    try:
        from bson import ObjectId
        from phoenix_portfolio.backend.mongo_client import db

        doc = db["emotional_fragments"].find_one({
            "_id": ObjectId(id),
            "user_id": user["user_id"],
        })

        if not doc:
            raise HTTPException(status_code=404, detail="Grind scan not found")

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

