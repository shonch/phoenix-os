# backend/routes/emotion_routes.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from backend.schemas.emotion import EmotionLogCreate, EmotionLogResponse
from backend.mongo_client import db
from backend.modules.symbolic_tag import normalize_tag
from bson import ObjectId

router = APIRouter(prefix="/emotions", tags=["Emotions"])

def get_current_user():
    # Placeholder for JWT or auth integration
    return {"user_id": "demo_user"}

# -------------------------
# CREATE
# -------------------------
@router.post("/", response_model=EmotionLogResponse)
def log_emotion(entry: EmotionLogCreate, user=Depends(get_current_user)):
    try:
        normalized_tags = [normalize_tag(t) for t in entry.tags]
        doc = {
            "subject": entry.subject,
            "tags": normalized_tags,
            "weather": entry.weather,
            "content": entry.content,
            "fragments": [f.dict() for f in entry.fragments] if entry.fragments else [],
            "timestamp": datetime.utcnow(),
            "user_id": user["user_id"],
        }
        result = db["fragments"].insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# READ (LIST)
# -------------------------
@router.get("/", response_model=list[EmotionLogResponse])
def get_emotions(user=Depends(get_current_user)):
    try:
        docs = list(db["fragments"].find({"user_id": user["user_id"]}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# READ (SINGLE)
# -------------------------
@router.get("/{id}", response_model=EmotionLogResponse)
def get_emotion(id: str, user=Depends(get_current_user)):
    try:
        doc = db["fragments"].find_one({"_id": ObjectId(id), "user_id": user["user_id"]})
        if not doc:
            raise HTTPException(status_code=404, detail="Emotion not found")
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# UPDATE
# -------------------------
@router.put("/{id}", response_model=EmotionLogResponse)
def update_emotion(id: str, entry: EmotionLogCreate, user=Depends(get_current_user)):
    try:
        normalized_tags = [normalize_tag(t) for t in entry.tags]
        update_doc = {
            "subject": entry.subject,
            "tags": normalized_tags,
            "weather": entry.weather,
            "content": entry.content,
            "fragments": [f.dict() for f in entry.fragments] if entry.fragments else [],
            "updated_at": datetime.utcnow(),
            "user_id": user["user_id"],
        }
        result = db["fragments"].update_one(
            {"_id": ObjectId(id), "user_id": user["user_id"]},
            {"$set": update_doc}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Emotion not found")
        updated = db["fragments"].find_one({"_id": ObjectId(id)})
        updated["id"] = str(updated["_id"])
        del updated["_id"]
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# DELETE
# -------------------------
@router.delete("/{id}")
def delete_emotion(id: str, user=Depends(get_current_user)):
    try:
        result = db["fragments"].delete_one({"_id": ObjectId(id), "user_id": user["user_id"]})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Emotion not found")
        return {"status": "deleted", "id": id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
