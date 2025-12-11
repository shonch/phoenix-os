# backend/routes/search_routes.py
from fastapi import APIRouter, Query, Depends, HTTPException
from backend.mongo_client import db

router = APIRouter(prefix="/search", tags=["Search"])

def get_current_user():
    return {"user_id": "demo_user"}  # replace with JWT later

@router.get("/")
def search_all(q: str = Query(..., description="Search term across all collections"),
               user=Depends(get_current_user)):
    try:
        matches = []
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            for doc in collection.find({"user_id": user["user_id"]}):
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
