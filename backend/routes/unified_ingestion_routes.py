# phoenix_portfolio/backend/routes/unified_ingestion_routes.py

from fastapi import APIRouter, HTTPException, Depends
from phoenix_portfolio.backend.services.ingestion import ingest_fragment
from phoenix_portfolio.backend.rituals.ritual_map import ritual_map
from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from phoenix_portfolio.backend.services.classifier import classify_ritual_type
from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/rituals", tags=["Unified Ritual Ingestion"])

def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}

@router.post("/ingest/")
def unified_ingest(payload: dict, user=Depends(get_current_user_id)):
    print("🔥 Phoenix Invocation: Unified Ingestion")

    # 1. Classify ritual type
    ritual_type = classify_ritual_type(payload)
    print(f"🔮 Classified Ritual Type: {ritual_type}")

    # 2. Lookup builder
    builder = ritual_map.get(ritual_type)
    if not builder:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ritual '{ritual_type}'. The stones do not recognize this name."
        )

    try:
        # 3. Build FragmentLogRequest
        req: FragmentLogRequest = builder(payload)

        # 4. Ingest
        fragment = ingest_fragment(req, user_id=user["user_id"])

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

