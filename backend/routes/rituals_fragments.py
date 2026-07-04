# phoenix_portfolio/backend/routes/rituals_fragments.py

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
import logging

from ..schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
)

from ..services.emotion_ingestion import ingest_fragment
from ..persistence.fragments import (
    get_all_fragments,
    get_fragment_by_id,
    search_fragments,
    get_fragments_by_tag,
)

router = APIRouter(prefix="/rituals/fragments", tags=["rituals_fragments"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Canonical ingestion endpoint
# ---------------------------------------------------------

@router.post("/log_emotion", response_model=FragmentResponse)
def log_emotion_route(payload: FragmentLogRequest) -> FragmentResponse:
    """
    Canonical ingestion endpoint.
    Accepts strict FragmentLogRequest payloads.
    """
    try:
        return ingest_fragment(payload)
    except Exception as e:
        logger.exception("Failed to ingest emotional fragment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INGESTION_ERROR",
                "message": "Failed to ingest emotional fragment",
                "details": str(e),
            },
        )


# ---------------------------------------------------------
# Minimal ingestion alias
# ---------------------------------------------------------

@router.post("/log", response_model=FragmentResponse)
def log_fragment(payload: FragmentLogRequest) -> FragmentResponse:
    """
    Alias for /log_emotion.
    """
    try:
        return ingest_fragment(payload)
    except Exception as e:
        logger.exception("Failed to ingest fragment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INGESTION_ERROR",
                "message": "Failed to ingest fragment",
                "details": str(e),
            },
        )


# ---------------------------------------------------------
# Fragment retrieval
# ---------------------------------------------------------

@router.get("/", response_model=list[FragmentResponse])
def list_fragments():
    try:
        return get_all_fragments()
    except Exception as e:
        logger.exception("Failed to list fragments")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to list fragments", "details": str(e)},
        )


@router.get("/search", response_model=list[FragmentResponse])
def search(query: str):
    try:
        return search_fragments(query)
    except Exception as e:
        logger.exception("Search failed")
        raise HTTPException(
            status_code=500,
            detail={"message": "Search failed", "details": str(e)},
        )


@router.get("/by_tag/{label}", response_model=list[FragmentResponse])
def fragments_by_tag(label: str):
    try:
        return get_fragments_by_tag(label)
    except Exception as e:
        logger.exception("Failed to fetch fragments by tag")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to fetch fragments by tag", "details": str(e)},
        )


# ---------------------------------------------------------
# Dynamic route LAST — so it doesn't swallow /search
# ---------------------------------------------------------

@router.get("/{fragment_id}", response_model=FragmentResponse)
def get_fragment(fragment_id: str):
    if not ObjectId.is_valid(fragment_id):
        raise HTTPException(status_code=400, detail="Invalid fragment ID")

    fragment = get_fragment_by_id(fragment_id)
    if not fragment:
        raise HTTPException(status_code=404, detail="Fragment not found")

    return fragment

