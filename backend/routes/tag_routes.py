# phoenix_portfolio/backend/routes/tag_routes.py

from fastapi import APIRouter, Depends, HTTPException

from phoenix_portfolio.phoenix_platform.auth import verify_token
from phoenix_portfolio.backend.modules import symbolic_tag

router = APIRouter(prefix="/tags", tags=["Tags"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.post("/create")
def create_tag_route(payload: dict, user=Depends(get_current_user_id)):
    """
    Creates (or updates, if the same label+user already exists) a real,
    permanent tag in the symbolic_tags collection.
    """
    try:
        tag_data = dict(payload)
        tag_data["user_id"] = user["user_id"]

        created = symbolic_tag.create_tag(tag_data)
        return created

    except ValueError as e:
        # create_tag raises ValueError if 'name' or 'user_id' is missing
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
