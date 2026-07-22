from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from phoenix_portfolio.backend.schemas.grind import GrindCreate
from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest, FragmentResponse
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/grind", tags=["Grind"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/", response_model=FragmentResponse)
def log_grind(entry: GrindCreate, user=Depends(get_current_user_id)):
    """
    Grind ingestion using the unified PhoenixTag-aware ingestion wrapper.
    """
    try:
        req = FragmentLogRequest(
            module="grind",
            type="grind_scan",
            layer="emotional",

            # grind-specific fields
            title=entry.title,
            subject=entry.subject,
            content=entry.note,
            weather=entry.weather,

            # tags (strings or Tag objects)
            tags=entry.tags + ["grind"],

            # optional body field
            body=entry.note,

            # module-specific payload
            extra={
                "intensity": entry.intensity,
                "urgency": entry.urgency,
                "state": entry.state,
                "sleep": entry.sleep,
                "status": entry.status,
            },

            # source override (optional)
            source="grind_routes",
        )

        return ingest_fragment(req, user_id=user["user_id"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

