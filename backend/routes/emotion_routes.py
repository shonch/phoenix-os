# phoenix_portfolio/backend/routes/emotion_routes.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId

from phoenix_portfolio.backend.schemas.emotion import (
    EmotionLogCreate,
    EmotionLogResponse,
)
from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.modules.symbolic_tag import (
    normalize_tag,
    suggest_tags,
    create_tag,
)
from phoenix_portfolio.backend.utils.serialization import (
    serialize_doc,
    serialize_docs,
)

from phoenix_portfolio.phoenix_platform.auth import verify_token

router = APIRouter(prefix="/emotions", tags=["Emotions"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


def _build_tags(raw_tags: list[str], user_id: str) -> list[str]:
    final_tags = []

    for raw in raw_tags:
        normalized = normalize_tag(raw)
        suggestions = suggest_tags(normalized)
        chosen = suggestions[0]["tag_name"] if suggestions else normalized
        final_tags.append(chosen)

        create_tag({
            "tag_name": chosen,
            "emoji": "💠",
            "archetype": "emotion",
            "sass_level": 0,
            "emotional_weight": "neutral",
            "color": "#77aaff",
            "source_system": "emotion_routes",
            "description": "Auto-inserted from emotion_routes",
            "dominatrix_affinity": [],
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
        })

    return final_tags


@router.post("/", response_model=EmotionLogResponse)
def log_emotion(entry: EmotionLogCreate, user=Depends(get_current_user_id)):
    try:
        timestamp = datetime.utcnow()
        user_id = user["user_id"]

        # Normalize + symbolic tags
        final_tags = _build_tags(entry.tags, user_id=user_id)

        # Markdown content
        md_content = f"""### 💠 Emotion Log (Legacy v1)

**Subject**: {entry.subject}  
**Weather**: {entry.weather or "N/A"}  
**Timestamp**: {timestamp.isoformat()}  

---

{entry.content or ""}

---

### Embedded Fragments
{entry.fragments or "None"}
"""

        doc = {
            "subject": entry.subject,
            "tags": final_tags,
            "weather": entry.weather,
            "content": md_content,
            "payload": {
                "subject": entry.subject,
                "weather": entry.weather,
                "content_raw": entry.content,
                "fragments": [f.dict() for f in entry.fragments] if entry.fragments else [],
            },
            "timestamp": timestamp,
            "type": "emotion_log_v1",
            "source_system": "emotion_routes_legacy",
            "legacy": True,
            "user_id": user_id,
        }

        result = db["emotional_fragments"].insert_one(doc)
        doc["_id"] = result.inserted_id

        return serialize_doc(doc)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[EmotionLogResponse])
def get_emotions(user=Depends(get_current_user_id)):
    try:
        docs = list(db["emotional_fragments"].find({
            "type": "emotion_log_v1",
            "user_id": user["user_id"],
        }))
        return serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=EmotionLogResponse)
def get_emotion(id: str, user=Depends(get_current_user_id)):
    try:
        doc = db["emotional_fragments"].find_one({
            "_id": ObjectId(id),
            "type": "emotion_log_v1",
            "user_id": user["user_id"],
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Emotion not found")
        return serialize_doc(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

