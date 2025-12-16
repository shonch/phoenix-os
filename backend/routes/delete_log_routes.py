# backend/routes/delete_log_routes.py
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.delete_log import DeleteLogCreate, DeleteLogResponse
from backend.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/delete_log", tags=["Delete Log"])

def get_current_user():
    # Placeholder for JWT or auth integration
    return {"user_id": "demo_user"}

# -------------------------
# CREATE (record a deletion event)
# -------------------------
@router.post("/", response_model=DeleteLogResponse)
def log_deletion(entry: DeleteLogCreate, user=Depends(get_current_user)):
    doc = {
        "fragment_id": entry.fragment_id,
        "fragment_type": entry.fragment_type,
        "reason": entry.reason,
        "timestamp": datetime.utcnow(),
        "user_id": user["user_id"],
    }
    result = db["deleted_fragments"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

# -------------------------
# READ (LIST)
# -------------------------
@router.get("/", response_model=list[DeleteLogResponse])
def list_deletions(user=Depends(get_current_user)):
    docs = list(db["deleted_fragments"].find({"user_id": user["user_id"]}))
    return serialize_docs(docs)

# -------------------------
# READ (SINGLE)
# -------------------------
@router.get("/{id}", response_model=DeleteLogResponse)
def get_deletion(id: str, user=Depends(get_current_user)):
    doc = db["deleted_fragments"].find_one({"_id": ObjectId(id), "user_id": user["user_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Delete log not found")
    return serialize_doc(doc)
