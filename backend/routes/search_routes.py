# phoenix_portfolio/backend/routes/search_routes.py

from fastapi import APIRouter, Query, Depends, HTTPException

# Shared JWT auth (Phoenix v2)
from phoenix_portfolio.phoenix_platform.auth import verify_token

# Canonical DB connector
from phoenix_portfolio.backend.mongo_client import db

router = APIRouter(prefix="/search", tags=["Search"])


# 🔐 Real user dependency (JWT-backed)
def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.get("/")
def search_all(
    q: str = Query(..., description="Search term across all collections"),
    user=Depends(get_current_user_id)
):
    try:
        matches = []
        user_id = user["user_id"]

        for collection_name in db.list_collection_names():
            collection = db[collection_name]

            # Only search documents belonging to the current user
            for doc in collection.find({"user_id": user_id}):
                # Check if the query appears in ANY field
                if any(q.lower() in str(value).lower() for value in doc.values()):
                    doc.pop("_id", None)
                    snippet = str(doc.get("content", ""))[:200].replace("\n", " ")

                    matches.append({
                        "collection": collection_name,
                        "subject": doc.get("subject"),
                        "tags": doc.get("tags"),
                        "date": doc.get("timestamp"),
                        "snippet": snippet,
                        **doc
                    })

        return matches

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

