from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.db import db
from phoenix_portfolio.backend.rituals.ritual_map import ritual_map

router = APIRouter(prefix="/rituals", tags=["rituals"])

# ——————————————————————————————————————————
# PHOENIX INGESTION GATE
# The torches ignite. The circle closes.
# ——————————————————————————————————————————
@router.post("/ingest")
async def ingest_fragment(ritual_type: str, payload: dict):
    print(f"🔥 Phoenix Invocation: {ritual_type}")

    ritual_handler = ritual_map.get(ritual_type)
    if not ritual_handler:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ritual '{ritual_type}'. The stones do not recognize this name."
        )

    try:
        fragment = await ritual_handler(payload)

        return {
            "status": "ok",
            "message": "✨ The ritual is complete. The fragment has been accepted into the Archive of Fire.",
            "fragment": fragment
        }

    except Exception as e:
        print("❌ Ritual Failure:", e)
        raise HTTPException(
            status_code=500,
            detail=f"⚡ The ritual faltered. The circle shuddered. {str(e)}"
        )

