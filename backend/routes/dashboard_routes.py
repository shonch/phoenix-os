# phoenix_portfolio/backend/routes/dashboard_routes.py

from fastapi import APIRouter, Depends, HTTPException

from phoenix_portfolio.phoenix_platform.auth import verify_token
from phoenix_portfolio.backend.engines.dashboard_engine import build_dashboard_state

router = APIRouter(prefix="/phoenix/dashboard", tags=["Phoenix Dashboard"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.get("/")
def dashboard(user=Depends(get_current_user_id)):
    """
    Phoenix Dashboard — unified summary built from the new analysis layer.
    No manual collection queries. No legacy V1/V2 schema assumptions.
    """
    try:
        return build_dashboard_state(user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

