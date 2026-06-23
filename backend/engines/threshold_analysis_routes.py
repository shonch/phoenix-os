# phoenix_portfolio/backend/routes/threshold_analysis_routes.py

from fastapi import APIRouter, Depends, HTTPException

from phoenix_portfolio.phoenix_platform.auth import verify_token
from phoenix_portfolio.backend.engines.threshold_emerge_engine import analyze_thresholds

router = APIRouter(prefix="/thresholds", tags=["Threshold Analysis"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.get("/analysis")
def thresholds_analysis(user=Depends(get_current_user_id)):
    try:
        return analyze_thresholds(user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

