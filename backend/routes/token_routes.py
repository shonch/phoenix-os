from fastapi import APIRouter
from phoenix_portfolio.phoenix_platform.auth import create_access_token

router = APIRouter(prefix="/phoenix", tags=["Phoenix Token"])

@router.get("/token")
def get_token():
    # This is the ONLY token the frontend actually uses.
    # It must match the user_id stored in MongoDB.
    token = create_access_token({"sub": "shonh@icloud.com"})
    return {"token": token}

