from fastapi import APIRouter
from phoenix_portfolio.backend.services.classifier import classify_ritual_type

router = APIRouter(prefix="/rituals", tags=["Ritual Classification"])

@router.post("/classify/")
def classify(payload: dict):
    ritual_type = classify_ritual_type(payload)
    return {"ritual_type": ritual_type}

