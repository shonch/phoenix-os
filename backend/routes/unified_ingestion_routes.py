# phoenix_portfolio/backend/routes/unified_ingestion_routes.py

from fastapi import APIRouter, HTTPException, Depends
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.backend.rituals.ritual_map import ritual_map
from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/rituals", tags=["Unified Ritual Ingestion"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/ingest/")
def unified_ingest(payload: dict, user=Depends(get_current_user_id)):
    """
    PhoenixOS v1.2 Unified Ritual Ingestion Route

    - Accepts full rich fragment from frontend (builder.ts)
    - Trusts the ritual_type already determined at /rituals/classify/
    - Selects correct ritual builder
    - Wraps fragment into FragmentLogRequest
    - Persists via ingest_fragment
    - Returns full FragmentResponse
    """

    print("🔥 Phoenix Invocation: Unified Ingestion")
    user_id = user["user_id"]

    # 1. Trust the ritual type already determined at /rituals/classify/ —
    # do not re-classify here. By ingest time, the step array has already
    # been swapped to the classified ritual's own prompts, so re-running
    # the classifier here would evaluate different text than what was
    # originally classified, producing inconsistent results.
    ritual_type = payload.get("ritual_type", "emotion")
    print(f"🔮 Using Ritual Type: {ritual_type}")

    # 2. Lookup correct ritual builder
    builder = ritual_map.get(ritual_type)
    if not builder:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ritual '{ritual_type}'. The stones do not recognize this name."
        )

    try:
        # 3. Build FragmentLogRequest from rich fragment
        req: FragmentLogRequest = builder(payload)

        # 4. Ingest into Phoenix Archive
        fragment = ingest_fragment(req, user_id=user_id)

        return {
            "status": "ok",
            "ritual_type": ritual_type,
            "message": "✨ The ritual is complete. The fragment has been accepted into the Archive of Fire.",
            "fragment": fragment
        }

    except Exception as e:
        print("❌ Ritual Failure:", e)
        raise HTTPException(
            status_code=500,
            detail=f"⚡ The ritual faltered. The circle shuddered. {str(e)}"
        )
