# phoenix_portfolio/backend/routes/grief_analysis_routes.py

from fastapi import APIRouter, Depends, HTTPException

from phoenix_portfolio.phoenix_platform.auth import verify_token
from phoenix_portfolio.backend.engines.grief_engine import analyze_grief

router = APIRouter(prefix="/grief", tags=["Grief Analysis"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.get("/analysis")
def grief_analysis(user=Depends(get_current_user_id)):
    try:
        return analyze_grief(user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

