# phoenix_portfolio/backend/routes/rituals_fragments.py

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from ..schemas.api_fragments import (
    FragmentLogRequest,
    FragmentResponse,
    Tag,
)

from ..services.emotion_ingestion import ingest_fragment
from ..persistence.fragments import (
    get_all_fragments,
    get_fragment_by_id,
    search_fragments,
    get_fragments_by_tag,
)

router = APIRouter(prefix="/rituals/fragments", tags=["rituals_fragments"])


@router.post("/log_emotion", response_model=FragmentResponse)
def log_emotion_route(payload: FragmentLogRequest) -> FragmentResponse:
    try:
        return ingest_fragment(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INGESTION_ERROR",
                "message": "Failed to ingest emotional fragment",
                "details": str(e),
            },
        )


@router.get("/", response_model=list[FragmentResponse])
def list_fragments():
    try:
        return get_all_fragments()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to list fragments", "details": str(e)},
        )


# ---------------------------------------------------------
# IMPORTANT: static routes BEFORE dynamic /{fragment_id}
# ---------------------------------------------------------

@router.get("/search", response_model=list[FragmentResponse])
def search(query: str):
    try:
        return search_fragments(query)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Search failed", "details": str(e)},
        )


@router.get("/by_tag/{label}", response_model=list[FragmentResponse])
def fragments_by_tag(label: str):
    try:
        return get_fragments_by_tag(label)
    except Exception as e:
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

